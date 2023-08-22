%% This script parses the data and places them into three separate structs, which represent each intelligent tutor.
%% It outputs 'parsedData.mat' which contains these three structs

fileName = 'results.json'; % filename in JSON extension
fid = fopen(fileName); % Opening the file
raw = fread(fid,inf); % Reading the contents
str = char(raw'); % Transformation
fclose(fid); % Closing the file
data = jsondecode(str); % Using the jsondecode function to parse JSON from string

%% Initialize counts to zero
% p1 == pedagogical ability 1 (talking like a teacher)
% p2 == pedagogical ability 2 (understanding the student)
% p3 == pedagogical ability 3 (helpful to the student)
% A == Reply A is chosen
% B == Reply B is chosen
% C == I cannot tell is chosen
stTemplate = struct();
stTemplate.p1 = struct();
stTemplate.p1.A = 0; 
stTemplate.p1.B = 0; 
stTemplate.p1.C = 0; 

stTemplate.p2 = struct();
stTemplate.p2.A = 0;
stTemplate.p2.B = 0;
stTemplate.p2.C = 0;

stTemplate.p3 = struct();
stTemplate.p3.A = 0;
stTemplate.p3.B = 0;
stTemplate.p3.C = 0;

noKBCount = stTemplate;
partialKBCount = stTemplate;
fullKBCount = stTemplate;

%% Iterate through all questions
for i=1:35
    % Open the particular question
    curQ = data.(['q',num2str(i)]);

    % Separate out stage 3 results
    stage3 = curQ.stage3;
    
    % Iterate through all student participants
    for person='A':'D'
        % Iterate through all intelligent tutors
        for kbType=["no","partial","full"]
            % Format the comparison variable name as per the json file
            name = [convertStringsToChars(kbType),'KBvsDomainStudent',person];

            % Obtain the comparison. It will be a cell array if it's not
            % empty; otherwise, it will be an empty list
            ca = stage3.(name);

            % The following adds the reply count to the respect struct,
            % pedagogical ability, and intelligent tutor
            if iscell(ca)
                if strcmp(kbType,'no')
                    for j=1:3
                        noKBCount.(['p',num2str(j)]).(ca{j}) = noKBCount.(['p',num2str(j)]).(ca{j}) + 1;
                    end
                elseif strcmp(kbType,'partial')
                    for j=1:3
                        partialKBCount.(['p',num2str(j)]).(ca{j}) = partialKBCount.(['p',num2str(j)]).(ca{j}) + 1;
                    end
                else
                    for j=1:3
                        fullKBCount.(['p',num2str(j)]).(ca{j}) = fullKBCount.(['p',num2str(j)]).(ca{j}) + 1;
                    end
                end
            end

        end
    end



end


%% Save the resultant data
save parsedData.mat noKBCount partialKBCount fullKBCount