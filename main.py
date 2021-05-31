import glob
import os
from surrogateGeneration import SurrogateGeneration
import threading
import configparser


# threading
class PipeThread(threading.Thread):
    def __init__(self, threadName, subset, sg):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.subset = subset
        self.sg = sg

    # process files
    def run(self):
        print("starting {} with {} files".format(self.threadName, len(self.subset)))
        self.sg.collectFiles(self.subset, self.threadName)
        print('Exiting {}'.format(self.threadName))


# run surrogate generation for subsets of files
def runSurrogateGeneration(parameters):
    sg = SurrogateGeneration(parameters)
    files = glob.glob(os.path.join(parameters['settings']['path_input'], '**', '*.ann'), recursive=True)
    print('{} files to process'.format(len(files)))

    threadNr = int(parameters['settings']['threads'])
    threads = []
    for i in range(0, threadNr):
        thread = PipeThread("Thread-{}".format(str(i)), files[i::threadNr], sg)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    print('{} files processed'.format(sg.nrFiles))


# get configuration
def getConfig():
    config = configparser.ConfigParser()
    config.read('param.conf')
    return config


if __name__ == '__main__':
    runSurrogateGeneration(getConfig())
