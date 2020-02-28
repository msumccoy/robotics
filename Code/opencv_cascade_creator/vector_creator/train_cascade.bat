:: Ensure that the folder specified by the -data flag already exsist before running this file

:: Supposidly this is the size people generally train (20X20)
opencv_traincascaded -data tennis_ball20x20 -vec 4166positives20x20.vec -bg bg.txt -numPos 4000 -numNeg 2000 -numStages 15 -w 20 -h 20 

:: This will take longer than training a 20X20 data set
:: opencv_traincascaded -data tennis_ball50x50 -vec 4166positives50x50.vec -bg bg.txt -numPos 4000 -numNeg 2000 -numStages 15 -w 50 -h 50 

:: Procede with caution. May take an astronomical amount of time to train
:: opencv_traincascaded -data tennis_ball100x100 -vec 4166positives100x100.vec -bg bg.txt -numPos 4000 -numNeg 2000 -numStages 15 -w 100 -h 100 