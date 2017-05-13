from argparse import ArgumentParser
import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, '..')))
from scripts.utils import InputError, report_error


DESCRIPTION = 'csvtail - print header and last lines of input'
EXAMPLES = 'examples: cat file.csv | csvtail -n -100 skip first 100 rows and print file.csv till the end.'


BLOCK_SIZE = 1024


def tail(f, lines):
    first_byte = f.tell()
    f.seek(0, 2)
    end_byte = f.tell()

    current_byte = end_byte - BLOCK_SIZE
    s = []
    n_count = 0
    while n_count <= lines:
        if current_byte >= first_byte:
            f.seek(current_byte)
            block = f.read(BLOCK_SIZE)
            current_byte = current_byte - BLOCK_SIZE
            n_count = n_count + block.count('\n')
            s.append(block)
        else:
            f.seek(first_byte)
            block = f.read(BLOCK_SIZE - first_byte + current_byte)
            s.append(block)
            break
    return ''.join((''.join(reversed(s))).splitlines(True)[-lines:])


def function_csvtail(args):
    try:
        input_stream = open(args.file, 'r') if args.file else sys.stdin
        output_stream = open(args.output_file, 'w') if args.output_file else sys.stdout

        heading = input_stream.readline()
        output_stream.write(heading)

        if args.number_of_lines > 0:
            if input_stream == sys.stdin:
                queue = []
                for line in input_stream:
                    queue = queue[-args.number_of_lines+1:]
                    queue.append(line)
                output_stream.write(''.join(queue))
            else:
                # use tail function
                output_stream.write(tail(input_stream, args.number_of_lines))
        else:
            line = 'line'
            for _ in range(-args.number_of_lines):
                line = input_stream.readline()
                if line == '':
                    break
            # write rest lines
            while line != '':
                line = input_stream.readline()
                output_stream.write(line)
    except FileNotFoundError:
        report_error("File {} doesn't exist".format(args.file))
    except KeyboardInterrupt:
        pass
    except BrokenPipeError:
        # The following line prevents python to inform you about the broken pipe
        sys.stderr.close()
    except Exception as e:
        report_error('Caught unknown exception. Please report to developers: {}'.format(e))
    finally:
        try:
            input_stream.close()
            output_stream.close()
        except:
            pass

def parse_args():
    parser = ArgumentParser(description=DESCRIPTION, epilog=EXAMPLES)
    parser.add_argument('-n', '--number_of_lines', type=int, help='Number of last rows to print if positive '
                                                                  'NUMBER_OF_LINES. Else skips NUMBER_OF_LINES lines '
                                                                  'and prints till the end of input. Default 10.',
                        default=10)
    parser.add_argument('-o', '--output_file', type=str, help='Output file. stdout is used by default')
    parser.add_argument('file', nargs='?', help='File to read input from. stdin is used by default')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    function_csvtail(parse_args())