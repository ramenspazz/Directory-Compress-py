# TL;DR
directory_compress {#threads} {directory} {output name}
same effect (sans visual info, and a few useful but noncritical addons) as:
  'tar c {} | xz --threads={} > {}.tar.xz'
  
# Directory-Compress-py
A short script to compress entire directorys with xz compression and taking advantage of multicore systems.
