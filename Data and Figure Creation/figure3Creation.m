%% This script produces Figure 3 from Castleman and Turkcan (2023).
% Load the data
load('parsedData.mat')

% Define the figure and its size
f = figure(1);
f.Position = [50 50 540 950];

% Define the subplot names
caPedagogies = {'a)','b)','c)'}; % note, each subplot is a different pedagogy

%% Subplot 1 - Talking like a teacher
sp1 = subplot(3,1,1);

% Process and plot the bar plot table for this category
curCategory = 'p1';
caCategories = {'No Knowledge Base Access','Partial Knowledge Base Access','Full Knowledge Base Access'};
X = categorical(caCategories, caCategories);
X = reordercats(X, caCategories);

y = [[noKBCount.(curCategory).A,noKBCount.(curCategory).B,noKBCount.(curCategory).C]/sum([noKBCount.(curCategory).A,noKBCount.(curCategory).B,noKBCount.(curCategory).C]);
     [partialKBCount.(curCategory).A,partialKBCount.(curCategory).B,partialKBCount.(curCategory).C]/sum([partialKBCount.(curCategory).A,partialKBCount.(curCategory).B,partialKBCount.(curCategory).C]);
     [fullKBCount.(curCategory).A,fullKBCount.(curCategory).B,fullKBCount.(curCategory).C]/sum([fullKBCount.(curCategory).A,fullKBCount.(curCategory).B,fullKBCount.(curCategory).C]);] * 100;


b = bar(X, y,'BarWidth',0.5,'FaceColor','flat','LineWidth',1);
ax = gca;
ax.YGrid = 'on';
ax.GridLineStyle = ':';
ax.LineWidth = 1.5;

% Turn off ticks and side axes

set(gca,'xticklabel',{[]})
set(gca, 'box', 'off')

% Custom bar colors
customColors = [
    255 227 141;
    131 182 226;
    226 96 144]/255;

for i = 1:numel(b)
    b(i).FaceColor = customColors(mod(i,3)+1,:);
end

% Limit the bar plot size at 60
ylim([0,60]);


% Set titles, legends, and labels
title(caPedagogies{1},'FontName','TimesNewRoman','FontSize',16,'Position',[-0.298364128270219,60.30125523012554,1.4e-14]);

subCategories = {'Intelligent Tutor Preference','Domain Expert Preference','No Clear Preference'};
legend(subCategories,'location','ne','FontName','Times New Roman','FontSize',16)



% Set formatting and fonts
ytickformat(gca,'percentage');

set(gca,'FontName', 'Times New Roman');
set(sp1,'FontName','TimesNewRoman','FontSize',16);

xticklabel_fs = get(gca,'XTickLabel');
set(gca, 'XTickLabel', xticklabel_fs, 'FontName', 'Times New Roman');

yticklabel_fs = get(gca,'YTickLabel');
set(gca, 'YTickLabel', yticklabel_fs, 'FontName', 'Times New Roman');

%% Subplot 2 - Understanding the student
sp2 = subplot(3,1,2);

% Process and plot the bar plot table for this category
curCategory = 'p2';
caCategories = {'No Knowledge Base Access','Partial Knowledge Base Access','Full Knowledge Base Access'};
X = categorical(caCategories, caCategories);
X = reordercats(X, caCategories);

y = [[noKBCount.(curCategory).A,noKBCount.(curCategory).B,noKBCount.(curCategory).C]/sum([noKBCount.(curCategory).A,noKBCount.(curCategory).B,noKBCount.(curCategory).C]);
     [partialKBCount.(curCategory).A,partialKBCount.(curCategory).B,partialKBCount.(curCategory).C]/sum([partialKBCount.(curCategory).A,partialKBCount.(curCategory).B,partialKBCount.(curCategory).C]);;
     [fullKBCount.(curCategory).A,fullKBCount.(curCategory).B,fullKBCount.(curCategory).C]/sum([fullKBCount.(curCategory).A,fullKBCount.(curCategory).B,fullKBCount.(curCategory).C]);] * 100;

b = bar(X, y,'BarWidth',0.5,'FaceColor','flat','LineWidth',1);
ax = gca;
ax.YGrid = 'on';
ax.GridLineStyle = ':';
ax.LineWidth = 1.5;

% Turn off ticks and side axes
set(gca,'xticklabel',{[]})
set(gca, 'box', 'off')

% Set bar graph colors
for i = 1:numel(b)
    b(i).FaceColor = customColors(mod(i,3)+1,:);
end

% Limit y-axis at 60
ylim([0,60]);

% Label and title the plot
ylabel('Ratings Count (Percentage)','FontName','TimesNewRoman','FontSize',18);

title(caPedagogies{2},'FontName','TimesNewRoman','FontSize',16,'Position',[-0.298364128270219,60.30125523012554,1.4e-14]);

% Formatting and fonts
ytickformat(gca,'percentage')
set(sp2,'FontName','TimesNewRoman','FontSize',16);

xticklabel_fs = get(gca,'XTickLabel');
set(gca, 'XTickLabel', xticklabel_fs, 'FontName', 'Times New Roman');

yticklabel_fs = get(gca,'YTickLabel');
set(gca, 'YTickLabel', yticklabel_fs, 'FontName', 'Times New Roman');

%% Subplot 3 - Helping the student
sp3 = subplot(3,1,3);

% Process and plot the bar plot table for this category
curCategory = 'p3';
caCategories = {'No Knowledge Base Access','Partial Knowledge Base Access','Full Knowledge Base Access'};
X = categorical(caCategories, caCategories);
X = reordercats(X, caCategories);

y = [[noKBCount.(curCategory).A,noKBCount.(curCategory).B,noKBCount.(curCategory).C]/sum([noKBCount.(curCategory).A,noKBCount.(curCategory).B,noKBCount.(curCategory).C]);
     [partialKBCount.(curCategory).A,partialKBCount.(curCategory).B,partialKBCount.(curCategory).C]/sum([partialKBCount.(curCategory).A,partialKBCount.(curCategory).B,partialKBCount.(curCategory).C]);;
     [fullKBCount.(curCategory).A,fullKBCount.(curCategory).B,fullKBCount.(curCategory).C]/sum([fullKBCount.(curCategory).A,fullKBCount.(curCategory).B,fullKBCount.(curCategory).C]);] * 100;


b = bar(X, y,'BarWidth',0.5,'FaceColor','flat','LineWidth',1);
ax = gca;
ax.YGrid = 'on';
ax.GridLineStyle = ':';
ax.LineWidth = 1.5;

% Turn side axes off (keep x-axis though because we need x-labels)
set(gca, 'box', 'off')

% Set colors
for i = 1:numel(b)
    b(i).FaceColor = customColors(mod(i,3)+1,:);
end

% Set y-axis limit of 60
ylim([0,60]);

% Set labels
xlabel(sp3,'Knowledge Base Hierarchy','FontName','TimesNewRoman','FontSize',18);
title(caPedagogies{3},'FontName','TimesNewRoman','FontSize',16,'Position',[-0.298364128270219,60.30125523012554,1.4e-14]);

% Set formatting and fonts
ytickformat(gca,'percentage')

set(sp3,'FontName','TimesNewRoman','FontSize',16);

% Set the positions fo each subplot
offset = -0.29;
sp1.set('Position',[0.135118793099298 0.71593853427896 0.769881206900702 0.26306146572104]);
sp2.set('Position',[0.135118793099298 0.71593853427896+offset 0.769881206900702 0.26306146572104]);
sp3.set('Position',[0.135118793099298 0.71593853427896+2*offset 0.769881206900702 0.26306146572104]);

% Final formatting of subplot 3
xticklabel_fs = get(gca,'XTickLabel');
set(gca, 'XTickLabel', xticklabel_fs, 'FontName', 'Times New Roman');

yticklabel_fs = get(gca,'YTickLabel');
set(gca, 'YTickLabel', yticklabel_fs, 'FontName', 'Times New Roman');

set(findall(gcf,'type','text'), 'fontname', 'times');

% Save this plot as a pdf
print('figure3.pdf','-dpdf','-fillpage')