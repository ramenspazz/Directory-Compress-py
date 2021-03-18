import sys
import os
import threading
import time
import math
import multiprocessing

# assert sys.version_info >= (3, 7)

s_per_ns = 10**(-9)
update_rate = 5
cmd = 'tar c {} | xz --threads={} > {}.tar.xz'
bit_suffix = 'B'
bit_prefix = ['Gi','Mi','Ki','']
base = 1024
file_format = '.tar.xz'
animation_ascii =   ['[    ]',
                     '[=   ]',
                     '[==  ]',
                     '[=== ]',
                     '[====]']

def format_byte(number):
    out_str = ''
    n_temp = number
    for i in range(len(bit_prefix)):
        temp = math.floor(n_temp / base**(len(bit_prefix)-i-1))
        if not(temp == n_temp):
            out_str = out_str + ' {}{}'.format(temp,bit_prefix[i]+bit_suffix)
            n_temp = n_temp - temp * base**(len(bit_prefix)-i-1)
        else:
            out_str = out_str + ' 0{}'.format(bit_prefix[i]+bit_suffix)
    return out_str

def core_detect():
    # if the user machine has only 1 core, use that
    if multiprocessing.cpu_count() == 1:
        return(1)
    # else, use one less than the number of cores available. favors speed and keeps a thread open for other tasks
    else:
        return(multiprocessing.cpu_count()-1)

def compress():
    try:
    # Start checking the number of input arguments in sys.argv for len(sys.argv) equal to 1, 2, or 3.
        if len(sys.argv) == 1:
            print('Not enough arguments! Pass h or help for instructions.\n')
            return(-1)
    # Check if user requested help, and setup argument list
        elif sys.argv[1] == 'help' or sys.argv[1] == 'h':
            print('h or help, displays this help text.\nEnter input directory name, output filename, and optionally the number of threads to use for compression.\n')
            return(0)
        elif len(sys.argv) == 2:
            cores = core_detect()
            cmd_final = cmd.format(sys.argv[1],cores,sys.argv[1])
            out_file_name = sys.argv[1]
        elif len(sys.argv) == 3:
            cores = core_detect()
            cmd_final = cmd.format(sys.argv[1],cores,sys.argv[2])
            out_file_name = sys.argv[1]
        elif (len(sys.argv) == 4) and os.path.isdir(sys.argv[1]) :
            cores = sys.argv[3]
            cmd_final = cmd.format(sys.argv[1],sys.argv[3],sys.argv[2])
            out_file_name = sys.argv[2]
        # get an estimate of how large the directory beeing compressed is
        threadpool = []
        total_size = 0
        c_fsize = 0
        fout = 0
        count = 0
        # get the size of the uncompressed user-specified file directory
        for p, dirs, files in os.walk(sys.argv[1]):
            for f in files:
                fp = os.path.join(p, f)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
        if total_size == 0:
            print('Empty Directory or Directory with only empty/hidden files! Exiting...\n')
            return -1
        print("Original size: {}\nUsing {} threads.".format(format_byte(total_size), cores))
        # create thread for running compression in background, while displaying output via console using time.sleep(#s)
        threadpool.append(threading.Thread(target=os.system, args=(cmd_final,))) # add job threads to pool
        for t in threadpool: # start threads
            t.start()
        t_start = time.clock_gettime_ns(time.CLOCK_REALTIME)
        t_temp1 = t_start
        # start the display subroutine, updating the current progress at a frequency of 
        # 1/update_rate seconds  as available to the console
        while True:
            t_temp2 = time.clock_gettime_ns(time.CLOCK_REALTIME)
            if threading.active_count() > 1:
                if (t_temp2 - t_temp1) > 1/(s_per_ns * update_rate):
                    t_temp1 = t_temp2
                    c_time = t_temp2 - t_start
                    fout = os.path.getsize(out_file_name+file_format)
                    cur_char = animation_ascii[count % len(animation_ascii)]
                    count = count + 1
                    c_fsize = float(fout)/float(total_size)
                    msg = 'Elapsed Time:   {:6.0f}   Seconds   {}   File Size:   {} @ {:5.4f}'.format(math.floor(c_time*s_per_ns),cur_char,format_byte(fout),c_fsize)
                    print(msg, end="\r", flush=True)
                    time.sleep(0.01)
            else:
                t_end = time.clock_gettime_ns(time.CLOCK_REALTIME)
                fout  = os.path.getsize(sys.argv[1]+file_format)
                c_fsize = float(fout)/float(total_size)
                done_msg = 'Total time for completion: {:16.4f}   Seconds\nFile size:   {} @ {:5.4f} * Original Size\n'.format((t_end - t_start) * s_per_ns,format_byte(fout),c_fsize)
                sys.stdout.write("\r\033[K")
                print(done_msg, end="\r", flush=True)
                time.sleep(0.125)
                for t in threadpool:
                    t.join()
                return
    # except control+c break to properly exit        
    except KeyboardInterrupt:
        print('Exiting...\n')
        return

if __name__ == '__main__':
    compress()
