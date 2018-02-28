function timedResponse
%% Timed response experiment for EEG study
%     script = 'Experiment1_Condition1_FreeRT.txt';
%     subjectFolder = '000\B1'; %'001/B8'; 
% 
%     script = 'Experiment1_Condition2_DirectionCuedRT.txt'; % eg. 
%     subjectFolder = '000\B2'; %'001/B8';

    script = 'Experiment1_Condition1_FreeRT.txt';
%     subjectFolder = '000\B5'; %'001/B8'; 

%     script = 'Experiment1_Condition2_DirectionCuedRT.txt'; % eg. 
%     subjectFolder = '000\B6'; %'001/B8';
    subjectFolder = 'alex\B8'; %'001/B8';

%     cond = 1;
    %cond = 2;
    

    path = 'C:\TimedResponse\Data\';
    writeFolder = fullfile(path, subjectFolder);
    
    PsychDefaultSetup(2);
   % output = [1 0 0 0];
        
%Set defaults fsfsdfs
    monitor.width = 43.2;     monitor.height = 24; %values in cmp
    KbName('UnifyKeyNames'); escapeKey = KbName('ESCAPE');
    timeWindow = 0.2;   time = 0;

% define global variables for cursor display
    global x;    global y;  global photosensor;
     
%run initialization functions
    ai = initializeAnalog;
    do = initializeDigitalOutput;
    display = initializeDisplay(monitor);
    tFile = dlmread(script, '\t', 1, 0);
     
    %Parallel port initialization (uses drivers from http://apps.usd.edu/coglab/psyc770/IO64.html )
        %create an instance of the io64 object
        ioObj = io64;
        % initialize the interface to the inpoutx64 system driver
        status = io64(ioObj);
        % if status = 0, you are now ready to write and read to a hardware port
        address = hex2dec('378');          %standard LPT1 output port address
        %io64(ioObj,address,data_out);   %output command
        % when finished with the io64 object it can be discarded via
        % 'clear all', 'clear mex', 'clear io64' or 'clear functions' command.

%     fileID = fopen(script);
%     tFile = textscan(fileID,'%s %s %s %s %s %s %s %s %s');
  %  tFile = textscan(fileID,'%s %f %f %f %f %f %f %f %f');

%present start position
%     Screen('FillOval', display.window, display.start.color, [display.start.position-(display.start.radius*display.ppcm) display.start.position+(display.start.radius*display.ppcm)]);        
%     Screen('Flip', display.window);
    
%set digital level high for 1s to indicate beginning of data collection...
%      outputSingleScan(do,[1 0 0 0]);
%      pause(1);
%      outputSingleScan(do,[0 0 0 0]);
%      pause(3);
    
%create loop where hitting escape will exit the program...   
    trial = 1;
    while trial <=  size(tFile,1)
               
        io64(ioObj,address,0);
        
    %initialize digital channels...
%            outputSingleScan(do,[0 0 0 0]);
    % If the user is pressing escape then exit.
        [ keyIsDown, seconds, keyCode ] = KbCheck;
        if keyIsDown
            if keyCode(escapeKey)
                break;
            end
            KbReleaseWait;
        end
        display.trial = trial;
    
    %pull info for this trial...
%         thisTrial.trialCode =   num2str(tFile(trial,1));   
        %quick fix for leading 0's
%         while length(thisTrial.trialCode) < 4
%             thisTrial.trialCode = ['0' thisTrial.trialCode];
%         end
%         thisTrial.trialCode = [str2num(thisTrial.trialCode(1)), str2num(thisTrial.trialCode(2)), str2num(thisTrial.trialCode(3)), str2num(thisTrial.trialCode(4))] 
        thisTrial.trialCode =   tFile(trial,1);
        thisTrial.startx =      tFile(trial,2);
        thisTrial.starty =      tFile(trial,3);
        thisTrial.target1x =    tFile(trial,4);
        thisTrial.target1y =    tFile(trial,5);
        thisTrial.switchTime =  tFile(trial,6);
        thisTrial.target2x =    tFile(trial,7);
        thisTrial.target2y =    tFile(trial,8);
        thisTrial.switchTime2 = tFile(trial,9);
        
    %set & open log file
        if length(num2str(trial)) == 1,          
            file = ['trial00' num2str(trial) '.bin'];
        elseif length(num2str(trial)) == 2,
            file = ['trial0' num2str(trial) '.bin'];
        else 
            file = ['trial' num2str(trial) '.bin'];
        end

        fid1 = fopen(fullfile([path, subjectFolder],file),'w');

    %present start position
        Screen('FillOval', display.window, display.start.color, [display.start.position-(display.start.radius*display.ppcm) display.start.position+(display.start.radius*display.ppcm)]);        
        Screen('Flip', display.window); 
        
    %set/reset target on flag   
        targetCueOn = 0; 
        targetOn = 0;

    %add listener to check the analog inputs
        lh = ai.addlistener('DataAvailable',@(src, event)getData3(src, event, fid1));
        
    %add a delay from 300 - 1300ms (note: 200ms added after ai.StartBackground, so total will become 500-1500ms...)
         pause(((1300-300).*rand() + 300)/1000);
    % trigger the acquisition
        ai.startBackground
        pause(.200)
        startTime = 0; time = 0;
        startTime = GetSecs;
        io64(ioObj,address,thisTrial.trialCode); %mark trial has started (based on onset of visual cues)
        
%         outputSingleScan(do,[0 0 0 0]);   %set digital channel to show trial has started
      %  io64(ioObj,address,0);   %make sure parallel port is not sending any codes
        %trial loop...
            while 1,            
                %update cursor position
                display.cursor.position = ([(x*-1)/0.15625 (y*-1)/0.15625].*display.ppcm) + display.start.position;
                %readout of x y position
%                 output = [output; x y];
                %update display
                display = updateDisplay(display,time,thisTrial);
                
               if thisTrial.trialCode == 12,
                   if time >= thisTrial.switchTime/1000 && time < thisTrial.switchTime/1000 + timeWindow,
                       io64(ioObj,address,14); %signal for target cue on...
                   elseif time >= thisTrial.switchTime2/1000 && time < ((thisTrial.switchTime2/1000) + timeWindow)
                       io64(ioObj,address,126); %signal for target on...
                   else
                       io64(ioObj,address,0); %signal for target cue on...
                   end
               else
                   if time >= thisTrial.switchTime/1000 && time < ((thisTrial.switchTime/1000) + timeWindow)
                        io64(ioObj,address,128);
                   else
                      io64(ioObj,address,0);
                   end
               end
               time = GetSecs - startTime;     
               
               if time > 3
                  trial=trial+1;
                  break; 
               end
    %             getDistance(display,display.cursor.position,display.start.position)
            end %of trial loop

        ai.stop
        
        delete(lh)      
        fclose(fid1);
    end
    
%present start position
    Screen('FillOval', display.window, display.start.color, [display.start.position-(display.start.radius*display.ppcm) display.start.position+(display.start.radius*display.ppcm)]);        
    Screen('Flip', display.window); 
    
 %set digital level high for 1s to indicate end of data collection...
%     outputSingleScan(do,[1 0 0 0]);
%     pause(1);
%     outputSingleScan(do,[0 0 0 0]);
%     pause(3);   
    
    
    
    Screen('CloseAll');
    
return

function [ai] = initializeAnalog
    try
        %make sure drivers (NI DAQmax) are properly installed
        daq.getVendors
        %Check DAQ is plugged in and working: 
        daq.getDevices
        % Initialization of session ai (analog input)...
        ai = daq.createSession('ni') 
        ai.Rate = 1000;                                     
        %Analog input for measuring voltages from the force transducer
%         ai.addAnalogInputChannel('Dev1',[3,11,1,9],'Voltage'); 
        ai.addAnalogInputChannel('Dev1',[0,8,1,9,2,10,3,11,4,12,5,13,6,14,7,15],'Voltage');  
        %Analog input for measuring voltage from the photosensor
%         ai.addAnalogInputChannel('Dev1','ai15','Voltage'); 
        %Analog input for measuring voltage from the buzzer(?)
%         ai.addAnalogInputChannel('Dev1','ai6','Voltage'); 
        
        ai.IsContinuous = true;
      % set the 'DataAvailable' event to trigger after 200 samples?? (all samples)
        ai.NotifyWhenDataAvailableExceeds = 20;
        
    catch
        
    end
return

function [do] = initializeDigitalOutput
    try
        %make sure drivers (NI DAQmax) are properly installed
        daq.getVendors
        %Check DAQ is plugged in and working: 
        daq.getDevices
        % Initialization of session ai...
        do = daq.createSession('ni')
        do.Rate = 1000;  
       
        %Open digital channel for showing the trial has started/ended...
%         addDigitalChannel(do,'Dev1', 'Port1/Line0', 'OutputOnly');
%         %Open digital channels for showing that the buzzer is going off:
%         addDigitalChannel(do,'Dev1', 'Port1/Line1', 'OutputOnly');
%         addDigitalChannel(do,'Dev1', 'Port1/Line2', 'OutputOnly');
%         addDigitalChannel(do,'Dev1', 'Port1/Line3', 'OutputOnly');
        
        %Open digital channel for turning the buzzer on  and off...
        %initialize values as zeros...
%         outputSingleScan(do,[0 0 0 0]);
        
    catch
        
    end
return

function [display] = initializeDisplay(monitor)
%% setup visual display elements    
    display.cursor.color = [0 0 255];
    display.cursor.radius = 0.15;

    display.start.color = [200 200 200];
    %display.start.pos is set in code...
    display.start.radius = 0.25;
    
    display.target.color = [0 255 0];
    display.target.radius = 1;
    display.target.distance = [8 0];   %distance of target from start pos...

% Get the list of screens and choose the one with the highest screen number.
	display.screens=Screen('Screens');
	display.screenNumber=max(display.screens);
    display.window=Screen('OpenWindow',display.screenNumber, [0 0 0]);
    [display.width, display.height]=Screen('WindowSize', display.window);

    HideCursor()    
    display.start.position = [display.width/2 display.height/2];
    
% Calculate pixels per centimeter
    display.ppcm = display.width/monitor.width;
return

function [display] = updateDisplay(display,time,thisTrial)
%% update visual display elements
%     topPriorityLevel = MaxPriority(window);
% Priority(topPriorityLevel);
Priority(MaxPriority(display.window));


%present trial number
    Screen('DrawText', display.window, num2str(display.trial), 20, 20); 

    display.start.position = [(display.width/2)+(thisTrial.startx*display.ppcm) (display.height/2)+(thisTrial.starty*display.ppcm)];
    display.target.position = [display.start.position(1)+(thisTrial.target1x*display.ppcm) display.start.position(2)+(thisTrial.target1y*display.ppcm)];  
    display.target.position2 = [display.start.position(1)+(thisTrial.target2x*display.ppcm) display.start.position(2)+(thisTrial.target2y*display.ppcm)];  
    
    display.photosensorTarget.position = [(display.width/32)+(thisTrial.startx*display.ppcm) (display.height/2)+(thisTrial.starty*display.ppcm)];
    
    display.photosensorBackground.position = display.photosensorTarget.position;
    
    %present start position
        Screen('FillOval', display.window, display.start.color, [display.start.position-(display.start.radius*display.ppcm) display.start.position+(display.start.radius*display.ppcm)]);        
    
    %present white background behind photosensor target
        Screen('FillOval', display.window, [255 255 255] , [display.photosensorTarget.position-(display.target.radius*2*display.ppcm) display.photosensorTarget.position+(display.target.radius*2*display.ppcm)]);
            
    %present target & photosensor target
    if thisTrial.trialCode == 12,   %a cued direction trial...
        if time < thisTrial.switchTime/1000 %present initial photosensor target
            Screen('FillOval', display.window, [0 0 0] , [display.photosensorTarget.position-(display.target.radius*display.ppcm) display.photosensorTarget.position+(display.target.radius*display.ppcm)]);      
        elseif time >= thisTrial.switchTime/1000 && time < thisTrial.switchTime2/1000, %remove initial photosensor target, show cue in target location
            Screen('FillOval', display.window, display.target.color, [display.target.position2-(display.target.radius*display.ppcm) display.target.position2+(display.target.radius*display.ppcm)]);   
            Screen('FillOval', display.window, [0 0 0], [display.target.position2-((display.target.radius-0.1)*display.ppcm) display.target.position2+((display.target.radius-0.1)*display.ppcm)]);           
        elseif time >= thisTrial.switchTime2/1000, %show photosensor target and full cue signal
            Screen('FillOval', display.window, display.target.color, [display.target.position2-(display.target.radius*display.ppcm) display.target.position2+(display.target.radius*display.ppcm)]);   
            Screen('FillOval', display.window, [0 0 0] , [display.photosensorTarget.position-(display.target.radius*display.ppcm) display.photosensorTarget.position+(display.target.radius*display.ppcm)]);      
        end
        
    else
         if time < thisTrial.switchTime/1000   
            Screen('FillOval', display.window, display.target.color, [display.target.position-(display.target.radius*display.ppcm) display.target.position+(display.target.radius*display.ppcm)]);        
         else
            Screen('FillOval', display.window, display.target.color, [display.target.position2-(display.target.radius*display.ppcm) display.target.position2+(display.target.radius*display.ppcm)]);   
             %present photosensor target if time is appropriate
            Screen('FillOval', display.window, [0 0 0] , [display.photosensorTarget.position-(display.target.radius*display.ppcm) display.photosensorTarget.position+(display.target.radius*display.ppcm)]);              
         end 
    end
    %set cursor position
        Screen('FillOval', display.window, display.cursor.color, [display.cursor.position-(display.cursor.radius*display.ppcm) display.cursor.position+(display.cursor.radius*display.ppcm)]);          
       
    %refresh display
         Screen('Flip', display.window); 
Priority(0);
return

function [distance] = getDistance(display, positionA, positionB)

    distance = sqrt((positionA(1) - positionB(1))^2 + (positionA(2) - positionB(2))^2);
    distance = distance/display.ppcm
    
return
