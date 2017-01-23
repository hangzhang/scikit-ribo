#!/usr/bin/env python

## ----------------------------------------
## scikit-ribo
## ----------------------------------------
## a module for visualization riboseq data
## ----------------------------------------
## author: Han Fang
## contact: hanfang.cshl@gmail.com
## website: hanfang.github.io
## date: 10/28/2016
## ----------------------------------------

from __future__ import print_function, division
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import sys
import pandas as pd
import seaborn as sns
import numpy as np
import pybedtools as pbt
import argparse
import multiprocessing


class figures(object):
    ''' define a class for plotting figures
    '''
    def __init__(self, fn, output, processes):
        #self.geneName = name
        self.riboDf = pd.read_table(fn,  header=0)
        self.output = output
        self.processes = processes

    def plotCoverageOnGene(self, geneName):
        ## confirm the gene exist
        if geneName not in set(self.riboDf["gene_name"]):
            print("[error]\tthe database does not have gene: ", str(geneName), flush=True)
            return
        ## read the df and construct numpy array
        # geneName = self.geneName
        riboCnt = np.array(self.riboDf[self.riboDf["gene_name"] == geneName]["ribosome_count"])
        pairProb = np.array(self.riboDf[self.riboDf["gene_name"] == geneName]["pair_prob"])
        ## reverse the array if the strand is negative
        if self.riboDf.loc[self.riboDf["gene_name"] == geneName]["gene_strand"].values[0] == "-":
            riboCnt = riboCnt[::-1]
            pairProb = pairProb[::-1]
        ## sliding window average of the pair probability
        window = np.ones(5).astype(float)/5.0
        slidingWindowAvg = np.convolve(pairProb, window, mode="valid")

        ## plot the ribosome count along a transcript
        f, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
        f.suptitle(geneName)
        ax1.plot(riboCnt, sns.xkcd_rgb["denim blue"], lw = 2)
        #print( [item.get_text() for item in ax1.get_xticklabels()])
        #labels = range(-24, riboCnt.size+1)
        # [int(float(item.get_text()))-24 for item in ax1.get_xticklabels()]
        #ax1.set_xticklabels(labels)
        startCodonPos, stopCodonPos = 8, riboCnt.size-8
        ax1.axvline(startCodonPos, color="#999999",dashes=[3,2],zorder=-1)
        ax1.axvline(stopCodonPos ,color="#999999",dashes=[3,2],zorder=-1)
        ax1.set_ylabel("Ribosome counts")
        ax2 = plt.subplot(2, 1, 2)
        ax2.plot(pairProb, sns.xkcd_rgb["medium green"], label="Per codon pairing probability")
        ax2.plot(slidingWindowAvg, sns.xkcd_rgb["amber"], label="5 codon average probability")
        #ax2.set_xticklabels(labels)
        ax2.set_ylim([0,1])
        ax2.set_ylabel("Pairing probability")
        ax2.set_xlabel("Position in transcript (5' -> 3')")
        ax2.axvline(startCodonPos, color="#999999",dashes=[3,2],zorder=-1)
        ax2.axvline(stopCodonPos,color="#999999",dashes=[3,2],zorder=-1)
        ax2.legend()
        plt.gcf()
        plt.savefig(self.output + "/plots/" + str(geneName) + ".riboCount.pdf")
        plt.clf()
        plt.cla()
        plt.close(f)

    def plotAllGenes(self):
        ## loop over all genes and plot
        geneNames = set(self.riboDf["gene_name"])
        pool = multiprocessing.Pool(self.processes)
        pool.map(self.plotCoverageOnGene, geneNames)
        print("[status]\tFinished plotting all genes.", flush=True)


## ----------------------------------------
## main
## ----------------------------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="input data frame, required")
    parser.add_argument("-g", help="gene of interest, or type [all] - automatically plot all genes, required")
    parser.add_argument("-p", help="number of processes, Default: 1", default=1, type=int)
    parser.add_argument("-o", help="output path, required")
    ## check if there is any argument
    if len(sys.argv) <= 1:
        parser.print_usage()
        sys.exit(1)
    else:
        args = parser.parse_args()
    ## process the file if the input files exist
    if (args.i != None and args.g != None and args.o != None):
        print("[status]\tprocessing the input file: " + args.i, flush=True)
        df_fn = args.i
        gene_name = args.g
        processes = args.p
        output = args.o
        # create folders
        cmd = "mkdir -p " + output + "/plots"
        os.system(cmd)
        # all genes or one gene
        fig = figures(df_fn, output, processes)
        if gene_name != "all":
            print("[execute]\tplotting ribosome coverage for gene: " + str(gene_name), flush=True)
            fig.plotCoverageOnGene(gene_name)
        else:
            print("[execute]\tplotting ribosome coverage for each gene", flush=True)
            fig.plotAllGenes()
        ## end
        print("[status]\tPlotting module finished.", flush=True)

    else:
        print("[error]\tmissing argument", flush=True)
        parser.print_usage()