# About Directory-Compress-py
A short bash wrapper that calls a python-3 script ran from the /usr/local/bin/ to compress entire directorys with xz compression and taking advantage of multicore systems.

# TL;DR
directory_compress {directory} {output name} {#threads}
same effect (sans visual info, and a few useful but noncritical addons) as:
  'tar c {} | xz --threads={} > {}.tar.xz'
  

