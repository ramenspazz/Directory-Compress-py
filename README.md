# Directory-Compress-py
a short script to compress entire directorys with xz compression and taking advantage of multicore systems.
TL;DR
directory_compress {directory} {output name}
same effect as:
  'tar c {} | xz --threads={} > {}.tar.xz'
