import sys, time, struct
import numpy as np
from numpy import fft
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import casperfpga

def init_10g(fpga):
  mac_base0 = (2<<40) + (2<<32)
  dest_macff= 255*(2**40) + 255*(2**32) + 255*(2**24) + 255*(2**16) + 255*(2**8) + 255
  arp_table = [dest_macff for i in range(256)]  
  dest_ip = 192*(2**24) + 168*(2**16) + 11*(2**8) + 4

  fpga.write_int('eth_rst',1)
  fpga.write_int('est_rst_sync',1)
  
  fpga.write_int('dest_ip',dest_ip)
  fpga.write_int('dest_port',4000)

  fpga_gbe = fpga.gbes['gbe0']
  fpga_gbe.configure_core(mac_base0+1,'192.168.11.33',4001)

  fpga.write_int('eth_rst',0)
  fpga.write_int('eth_en',1)
  fpga.write_int('est_rst_sync',0)

  fpga.write_int('sync',1)

def get_vacc_data(fpga, nchannels=2, nfft=16384):
  acc_n = fpga.read_uint('acc_cnt')
  chunk = nfft//nchannels

  raw = np.zeros((nchannels, chunk))
  for i in range(nchannels):
    raw[i,:] = struct.unpack('>{:d}Q'.format(chunk), fpga.read('q{:d}'.format((i+1)),chunk*8,0))

  interleave_q = []
  for i in range(chunk):
    for j in range(nchannels):
      interleave_q.append(raw[j,i])

  return acc_n, np.array(interleave_q, dtype=np.float64)

def plot_spectrum(fpga, num_acc_updates=None):

  fig = plt.figure()
  ax = fig.add_subplot(111)
  ax.grid();

  # design parameters
  fs = 491.52
  Nfft = 2**16
  fbins = np.arange(0, Nfft//2)
  df = fs/Nfft
  nchannels = 2
  faxis = fbins*df

  # casper fft only outputs positive bins so tell the readout code to only expect half the channels
  acc_n, spectrum = get_vacc_data(fpga, nchannels=nchannels, nfft=Nfft//2)
  line, = ax.plot(faxis,10*np.log10(spectrum),'-')

  ax.set_xlabel('Frequency (MHz)')
  ax.set_ylabel('Power (dB arb.)')

  def update(frame, *fargs):
    acc_n, spectrum = get_vacc_data(fpga, nchannels=nchannels, nfft=Nfft//2)
    line.set_ydata(10*np.log10(spectrum))

    ax.set_title('acc num: %d' % acc_n)

  v = anim.FuncAnimation(fig, update, frames=1, repeat=True, fargs=None, interval=1000)
  plt.show()

def plot_adc(fpga):
  fig = plt.figure()
  ax = fig.add_subplot(111)
  ax.grid();

  fpga.write_int('adc_snapshot_ss_ctrl',3)
  time.sleep(0.1)
  fpga.write_int('adc_snapshot_ss_ctrl',0)

  adc_dat = struct.unpack('>8192h', fpga.read('adc_snapshot_ss_bram',16384))
  plt.plot(adc_dat)
  plt.show()
  

if __name__=="__main__":
  from optparse import OptionParser

  p = OptionParser()
  p.set_usage('manas_spec.py <HOSTNAME_or_IP> [options]')
  p.set_description(__doc__)
  p.add_option('-l', '--acc_len', dest='acc_len', type='int',default=2*(2**28)//32768,
      help='Set the number of vectors to accumulate between dumps. default is 2*(2^28)/32768')
  p.add_option('-s', '--skip', dest='skip', action='store_true',
      help='Skip programming and begin to plot data')
  p.add_option('-b', '--fpg', dest='fpgfile',type='str', default='',
      help='Specify the fpg file to load')
  p.add_option('-a', '--adc', dest='adc_chan_sel', type=int, default=0,
      help='adc input to select values are 0,1,2, or 3')

  opts, args = p.parse_args(sys.argv[1:])
  if len(args) < 1:
    print('Specify a hostname or IP for your zcu111 CASPER platform.\n'
          'Run with the -h flag to see all options.')
    exit()
  else:
    hostname = args[0]

  if opts.fpgfile != '':
    bitstream = opts.fpgfile
  else:
    fpg_prebuilt = './prebuilt/manas_spec.fpg'

    print('using prebuilt fpg file at %s' % fpg_prebuilt)
    bitstream = fpg_prebuilt

  if opts.adc_chan_sel < 0 or opts.adc_chan_sel > 3:
    print('adc select must be 0,1,2, or 3')
    exit()

  print('Connecting to %s... ' % (hostname))
  fpga = casperfpga.CasperFpga(hostname)
  time.sleep(0.2)

  if not opts.skip:
    print('Programming FPGA with %s...'% bitstream)
    fpga.upload_to_ram_and_program(bitstream)
    print('done')
  #else:
  #  fpga.get_system_information()
  #  print('skip programming fpga...')

  print('Configuring accumulation period...')
  fpga.write_int('acc_len',opts.acc_len)
  time.sleep(0.1)
  print('done')

  print('setting capture on adc port %d' % opts.adc_chan_sel)
  fpga.write_int('adc_chan_sel', opts.adc_chan_sel)
  time.sleep(0.1)
  print('done')

  fpga.write_int('fft_shift',65535)

  print('Resetting counters...')
  fpga.write_int('cnt_rst',1) 
  fpga.write_int('cnt_rst',0) 
  time.sleep(3)

  print('trigger sync...')
  fpga.write_int('sync', 1)
  time.sleep(0.1)
  fpga.write_int('sync', 0)
  time.sleep(3)
  print('done')

  try:
    plot_spectrum(fpga)
    #plot_adc(fpga)
  except KeyboardInterrupt:
    exit()
