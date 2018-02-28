function getData3(src,event,fid)

 %set calibration matrix
       calibration = [-0.020559401 -0.006341148 0.043048497 -3.631807327 0.031158151 3.681540251;
                      -0.051654425	4.316632271	0.013176571	-2.104834795 0.019042328 -2.13189888];

% set the global time and data variables to pass data out of the callback function
%      global x;              x = mean(event.Data(:,1)) - mean(event.Data(:,2));
%      global y;              y = mean(event.Data(:,3)) - mean(event.Data(:,4));
%      global photosensor;    photosensor = mean(event.Data(:,5));
%      global buzzer;         buzzer = mean(event.Data(:,6));

       global x;             x = mean(event.Data(:,7)) - mean(event.Data(:,8));
       global y;             y = 0; %mean(event.Data(:,3)) - mean(event.Data(:,4));
       global photosensor;   photosensor = 0;
       global buzzer;        buzzer = 0;

       %stream analog channel data:
%        [mean(event.Data(:,1)) mean(event.Data(:,2)) mean(event.Data(:,3)) mean(event.Data(:,4)) mean(event.Data(:,5)) mean(event.Data(:,6)) mean(event.Data(:,7)) mean(event.Data(:,8)) mean(event.Data(:,9)) mean(event.Data(:,10)) mean(event.Data(:,11)) mean(event.Data(:,12)) mean(event.Data(:,13)) mean(event.Data(:,14)) mean(event.Data(:,15)) mean(event.Data(:,16))]
       
%        [mean(event.Data(:,1))-mean(event.Data(:,2)) mean(event.Data(:,3))-mean(event.Data(:,4)) mean(event.Data(:,5))-mean(event.Data(:,6)) mean(event.Data(:,7))-mean(event.Data(:,8)) mean(event.Data(:,9))-mean(event.Data(:,10)) mean(event.Data(:,11))-mean(event.Data(:,12)) mean(event.Data(:,13))-mean(event.Data(:,14)) mean(event.Data(:,15))-mean(event.Data(:,16))]
       
%     [mean(event.Data(:,7)) - (mean(event.Data(:,8) * calibration(1,:)))];


    %compensate for initial offset...
%        y = y + 0.13;
        x = x + 0.2;
     
     %transform x to get rid of y bias
%       x = x + (0.4669*y + 0.0142);
     
%      [x y photosensor buzzer]

     data = [event.TimeStamps, event.Data] ;

     fwrite(fid,data','double'); 
      

    %attempt to compensate for very low forces...
    %add a distance clause...
%     
%      if abs(x<1)
%         if x > 0,
%             x = power(x,2);
%         else
%             x = power(x,2)*-1;
%         end
%      end
% 
%      if abs(y<1)
%          if y > 0
%              y = power(y,2);
%          else
%              y = power(y,2)*-1;
%          end
%      end

   
end