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
        if len(sys.argv) == 1 and sys.argv[1]) == 'h':
            print('h displays help\nEnter number of threads to use for compression, input directory name, and output filename.\n')
            return
        elif(len(sys.argv) == 3) and os.path.isdir(sys.argv[1]):
            threadpool = []
            count = 0
            if multiprocessing.cpu_count() == 1:
                cores = 1
            else:
                cores = multiprocessing.cpu_count()-1
            cmd_final = cmd.format(sys.argv[1],cores,sys.argv[2])
            path = sys.argv[1]
            index = -1
            for n in range(0,len(path)):
                if path[len(path) - n - 1] == '/':
                    index =  len(path) - n - 1
                    break
            path = path[0:index]
            print(path+'/ is current path\n')
            total_size = 0
            c_fsize = 0
            fout = 0
            start_path = sys.argv[1]  # To get size of current directory
            for path, dirs, files in os.walk(start_path):
                for f in files:
                    fp = os.path.join(path, f)
                    total_size += os.path.getsize(fp)
            print("Original size: {}\nUsing {} threads.".format(format_byte(total_size), multiprocessing.cpu_count()-1))
            #os.system('touch {}'.format(path+file_format))
            threadpool.append(threading.Thread(target=os.system, args=(cmd_final,))) # add job threads to pool
            for t in threadpool: # start threads
                t.start()
            t_start = time.clock_gettime_ns(time.CLOCK_REALTIME)
            t_temp1 = t_start
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
    except KeyboardInterrupt:
        print('Exiting...\n')
        return

if __name__ == '__main__':
    main()
