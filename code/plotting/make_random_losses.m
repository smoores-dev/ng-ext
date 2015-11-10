%creates random losses for testing

fname = 'losses_test.txt';
fid= fopen(fname,'w');

nUsers = 60;
maxNumLevels = 5;
loss_increment = 5;

for i= 1:nUsers
    nLevels = ceil(rand()*maxNumLevels);
    losses = zeros(1,nLevels);
    loss = rand*loss_increment;
    fprintf(fid,'%d:',i); fprintf(fid,' %.2f',loss); fprintf(fid,'\n');

%     for j= 1:nLevels
%         loss = loss + rand*loss_increment;
%         losses(j) = loss;
%     end
%     fprintf(fid,'%d:',i); fprintf(fid,' %.2f',losses); fprintf(fid,'\n');
end