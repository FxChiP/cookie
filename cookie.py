#
# Originally written by Zach C. <fxchip@gmail.com>
#
# And released into the public domain. Requires Python 3.x and
# a UNIX environment (OS X and Linux seem to work)
#

import fcntl
import os
import select
import sys
import termios
import time
import tty


PROMPT = "cookie"
COOKIE_EMOJI = "🍪 "
SLEEPYTIME = .075

def main(argv=sys.argv):
    _prompted = ""
    _idx = -1 
    flags = termios.tcgetattr(sys.stdin)
    flags[3] = flags[3] & ~termios.ECHO
    termios.tcsetattr(sys.stdin, termios.TCSANOW, flags)
    tty.setcbreak(sys.stdin, termios.TCSANOW)
    ioflags = fcntl.fcntl(sys.stdin.fileno(), fcntl.F_GETFL)
    fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, ioflags & ~os.O_NONBLOCK)

    while _prompted != PROMPT:
        try:
            current_time = time.time()
            readies = select.select([sys.stdin], [sys.stdout], [], SLEEPYTIME)
            writes = readies[1]
            for writefd in writes:
                _idx = (_idx + 1) % len(PROMPT)
                if _idx == 0:
                    writefd.write(COOKIE_EMOJI + " " + PROMPT[_idx].upper() + " ")
                else:
                    writefd.write(PROMPT[_idx].upper() + " ")
                writefd.flush()
            offset = time.time() - current_time
            while offset <= SLEEPYTIME:
                readies = select.select([sys.stdin], [], [], SLEEPYTIME - offset)
                reads = readies[0]
                offset = time.time() - current_time
                for readfd in reads:
                    _prompted += readfd.read(1)
                    if not PROMPT.startswith(_prompted.lower().strip()):
                        _prompted = ""
                    else:
                        _prompted = _prompted.strip()
        except KeyboardInterrupt:
            # ah-ah-ah, you didn't say the magic word
            pass

    flags[3] = flags[3] | termios.ECHO
    termios.tcsetattr(sys.stdin, termios.TCSANOW, flags)

if __name__=="__main__":
    main()
