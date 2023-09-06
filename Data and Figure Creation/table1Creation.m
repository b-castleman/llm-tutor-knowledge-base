%% This script produces Table 1 from the paper Castleman and Turkcan (2024). The output table is a cell array titled "ca"
% Load the data
load('parsedData.mat')

%% Change the table from counts into percentages
% Hard code the question count
totalAssessmentPerIntelligentTutorCount = 70; % 35 questions total * 2 participants evaluating each answer

% For all pedagogical abilities
for pedagogy=1:3
    % For all intelligent tutors
    for intelligentTutor = {'no','partial','full'}
        % Get the intelligent tutor's structure
        structName = [intelligentTutor{1},'KBCount'];
        % For all reply types
        for reply = {'A','B','C'}
            % Change the count into the percentage for this intelligent
            % tutor-reply-pedagogy combination
            eval([structName,'.p',num2str(pedagogy),'.(reply{1}) = ',structName,'.p',num2str(pedagogy),'.(reply{1}) / totalAssessmentPerIntelligentTutorCount * 100;'])
        end
    end
end


%% Create Table
% Define column headers
ca = {'Reply A','Reply B','Reply C'};

% Iterate through all intelligent tutors
for intelligentTutor = {'no','partial','full'}

    % Get the intelligent tutor's struct
    st = eval([intelligentTutor{1},'KBCount;']);
    
    % Iterate through all pedagogies
    for pedagogy={'p1','p2','p3'}

        % Place this intelligent tutor's specific pedagogy replies into the
        % table
        ca(end+1,:) = {st.(pedagogy{1}).A, st.(pedagogy{1}).B,st.(pedagogy{1}).C};
    end
end

% Add row names and pedagogical categories
rowNames = {'';'No KB Access';'';'';'Partial KB Access';'';'';'Full KB Access';'';''};
pedagogyList = {'';'Talking like a teacher';'Understanding the student';'Helpful to the student';'Talking like a teacher';'Understanding the student';'Helpful to the student';'Talking like a teacher';'Understanding the student';'Helpful to the student'};
ca = [rowNames,pedagogyList,ca];

%% Print Table
ca

%% Save Table
writecell(ca,'table1.csv');
