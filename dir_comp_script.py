import sys
import os
import threading
import time
import math
import multiprocessing

assert sys.version_info >= (3, 7)

s_per_ns = 10**(-9)
up_per_sec = 5
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

def main():
    try:

    # Check if user requested help, and setup argument list
        args = []
        for val in sys.argv:
            args.append(val)

        if args[1] == 'help' or args[1] == 'h':
            print('h or help, displays this help text.\nEnter input directory name, output filename, and optionally the number of threads to use for compression.\n')
            return 0

    # Check if the number of arguments passed in the initial call directory_compress is equal to 2 or 3 (+1 in code for
    # script as argv[0]) and if it is true, check if the user specified the number of threads to use.
        elif (len(args) >= 3) and os.path.isdir(args[1]) :
            threadpool = []
            count = 0
#            print(len(args))
            if len(args) == 3: # auto select number of cores to use
                # if the user machine has only 1 core, use that
                if multiprocessing.cpu_count() == 1:
                    cores = 1
                # else, use one less than the number of cores available. favors speed and keeps a thread open for other tasks
                else:
                    cores = multiprocessing.cpu_count()-1
            else:
                cores = args[3]

            cmd_final = cmd.format(sys.argv[1],cores,args[2])

        # get an estimate of how large the directory beeing compressed is
            total_size = 0
            c_fsize = 0
            fout = 0
            for p, dirs, files in os.walk(args[1]):
                for f in files:
                    fp = os.path.join(p, f)
                    total_size += os.path.getsize(fp)
            # output origional size of directory being compressed
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
        # start the display subroutine to show progress, and realtime updates as available to the console
            while True:
                t_temp2 = time.clock_gettime_ns(time.CLOCK_REALTIME)
                if threading.active_count() > 1:
                    if (t_temp2 - t_temp1) > 1/(s_per_ns * up_per_sec):
                        t_temp1 = t_temp2
                        c_time = t_temp2 - t_start
                        fout = os.path.getsize(sys.argv[2]+file_format)
                        cur_char = animation_ascii[count % len(animation_ascii)]
                        count = count + 1
                        c_fsize = float(fout)/float(total_size)
                        msg = 'Elapsed Time:   {:6.0f}   Seconds   {}   File Size:   {} @ {:5.4f}'.format(math.floor(c_time*s_per_ns),cur_char,format_byte(fout),c_fsize)
                        print(msg, end="\r", flush=True)
                        time.sleep(0.01)
                else:
                    t_end = time.clock_gettime_ns(time.CLOCK_REALTIME)
                    fout  = os.path.getsize(sys.argv[2]+file_format)
                    c_fsize = float(fout)/float(total_size)
                    done_msg = 'Total time for completion: {:16.4f}   Seconds\nFile size:   {} @ {:5.4f} * Original Size\n'.format((t_end - t_start) * s_per_ns,format_byte(fout),c_fsize)
                    sys.stdout.write("\r\033[K")
                    print(done_msg, end="\r", flush=True)
                    time.sleep(0.125)
                    for t in threadpool:
                        t.join()
                    return

        elif len(sys.argv) == 0:
            print('Not enough arguments!\n')
            return
    # except cntrl+c break to properly exit        
    except KeyboardInterrupt:
        print('Exiting...\n')
        return

if __name__ == '__main__':
    main()
