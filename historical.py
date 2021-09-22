### Analyze Historical Calculations ###
import os
import glob


def historic():
    # Get a list of all the paths and base file names
    paths = glob.glob('data/output_*.csv')
    files = [os.path.basename(x) for x in paths]
    files.sort(reverse=True)

    print('done')


if __name__ == '__main__':
    historic()
