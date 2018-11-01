#!/usr/bin/env python

# ----------------------------------------------------------------------------------- #
#
#  Python/ROOT macro for training different types of TMVA's discriminants.
#
#  Author: Soufiane Zerradi
#  Email:  sfnzerradi@gmail.com
#  Date:   27/10/2018
#
#  
#
# ----------------------------------------------------------------------------------- #

from ROOT import *
import sys

# Main call here:
if __name__ == '__main__':


    # ----------------------------------------------------------------------------------- #
    # MVA using six variables:
    # ----------------------------------------------------------------------------------- #

    # Define path to input files, name of ttrees and cuts to be applied on signal and background .
    # Note that we here use the same input file and tree but with the "var_id" variable, but this
    # can in general be taken from several files (see Higgs example below).
    sigfile_name = '/skimmed/hp800/hp800.higgs.11466938._000001.out.root'
    sigtree_name = 'nominal_Loose'

    bkgfile_name = '/skimmed/ttbar/ttbar.higgs.11468615._000002.out.root'
    bkgtree_name = 'nominal_Loose'

    # Here is just defined a cut based on a rough eye estimate from looking at data
    # The names here should correspond to what is found in the ttrees 
    # SR64 -> nJets==6 && nBTags_70==4
    #cut = { 'signal'     : 'nJets>=6 && nBTags_70>=4 ' , 
            #'background' : 'nJets>=6 && nBTags_70>=4 ' }
    # SR63 -> nJets==6 && nBTags_70==3
    cut = { 'signal'     : 'nJets==6 && nBTags_70==3 ' , 
            'background' : 'nJets==6 && nBTags_70==3 ' }
    # Define which variables we want to use for classification
    # Use a dictionary to store both name and datatype
    vardict = {"dEtajj_MaxdEta": 'F',
               "HT_jets": 'F',
               "dRbb_MaxPt_70": 'F',
               "dRlepbb_MindR_70": 'F',
               "dRbb_MaxM_70": 'F',
               "Mbb_MindR_70": 'F'}





    # ----------------------------------------------------------------------------------- #
    # TMVA is defined from here...
    # ----------------------------------------------------------------------------------- #

    # Define factory options. See table 1 of the TMVA user guide for settings:
    #   http://tmva.sourceforge.net/docu/TMVAUsersGuide.pdf
    
    factoryOption = "!V:!Silent:Transformations=I;P:AnalysisType=Classification"

    # TMVA title : 
    tmvatitle = "TMVAClassifier"

    # Start training here:
    output  = TFile("./tmva." + tmvatitle + ".root", "RECREATE" )
    factory = TMVA.Factory( tmvatitle, output, factoryOption )

    # Retrieve signal and background data:
    file_signal = TFile( sigfile_name, "READ" )
    tree_signal = file_signal.Get( sigtree_name )
    file_background = TFile( bkgfile_name, "READ" )
    tree_background = file_background.Get( bkgtree_name )

    # Tell the TMVA factory where it should get the signal and background data from.
    # The second argument is an event weight if you e.g. have several background models.
    # When training, it is important that their relative abundance is correctly specified.
    factory.AddSignalTree(     tree_signal    , 1.0 )   # Tell tmva where it should find signal
    factory.AddBackgroundTree( tree_background, 1.0 )   # and background trees

    # Add variables to your factory:
    for ivar in vardict : 
        # This will tell the factory which variables should be used for
        # classification and their data format, e.g. 
        factory.AddVariable( ivar, ivar, "", vardict[ivar] )
        # weights  
        factory.SetWeightExpression("fabs(weight_leptonSF * weight_bTagSF_70 * weight_mc * weight_pileup * weight_jvt * weight_ttbb_Norm * weight_ttbb_Shape_SherpaNominal)")

    # Tell factory how many event it should train on etc.
    # First set of arguments tell the factory which cuts are to be applied on the signal and background data
    # Next are general training options, see table to of the TMVA user guide.
    # Here we have specified : use all signal event, all bacgkround events
    # To a random selection of these events to use for training and testing.
    factory.PrepareTrainingAndTestTree( TCut(cut['signal']), TCut(cut['background']), 
                                        "nTrain_Signal=0:nTrain_Background=0:SplitMode=Random:NormMode=NumEvents:!V" )

    # Define different types of classifiers
    factory.BookMethod( TMVA.Types.kFisher   , "Fisher"  , "!H:!V:Fisher:VarTransform=None")
   # factory.BookMethod( TMVA.Types.kBDT      , "BDT"     , "!H:!V:NTrees=10:MaxDepth=1:VarTransform=None" )
   # factory.BookMethod( TMVA.Types.kCFMlpANN , "CFMlpANN", "!H:!V:NCycles=10:HiddenLayers=N"  )

    # Execcute actual training here
    factory.TrainAllMethods();
    factory.TestAllMethods();
    factory.EvaluateAllMethods();

    # Write and close output file
    output.Write()
    output.Close()


# You can study the output by typing in your terminal (here it is started automatically!): 

# root -l $ROOTSYS/tmva/test/TMVAGui.C\(\"tmva.TMVAClassifier.root\"\)
