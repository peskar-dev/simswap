# crysto-roop 

### original: https://github.com/s0md3v/roop/tree/main/roop

## How to use

```python
# import the library
from roop.rooplib import core as lib

# Prepare target video:
# 1) creates temporary directory ./temp
# 2) extracts frames from the video to ./temp/vid
lib.prepare(
    target_path='./tests/vid.mp4',
)


# Generate video:
# 1) creates temporary directory ./temp/{random}
# 2) copy frames from ./tests/temp/vid to ./temp/{random}
# 3) process frames in ./temp/{random}
# 4) create video from processed frames to $output_path
# 5) remove ./temp/{random}
lib.run(
    source_path='./tests/source.jpg',
    target_path='./tests/vid.mp4',
    output_path='./outputs/output3.mp4',
)

```
