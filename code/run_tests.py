import os

training_set = []
for file_name in os.listdir('Data/Training/'):
    uid = file_name.split('.')[0]
    training_set.append(uid)

outs = []
submission = open('training_prediction1.csv', 'w')
submission.write('UserId,Predicted\n')
ins = open("submission.csv")
ins.readline()
for line in ins:
    uid, numFriends, circles = line.split(",")
    if uid in training_set:
        outs.append(uid)
        num_circles = circles.count(";") + 1
        submission.write("{0},{1},{2}".format(uid, num_circles, circles))
submission.close()

training_test = open('training_ground1.csv', 'w')
training_test.write('UserId,Predicted\n')
for file_name in os.listdir('Data/Training/'):
    uid = file_name.split('.')[0]
    if uid in outs:
        handle = open('Data/Training/' + file_name)
        circles = []
        for line in handle:
            circle = line.strip('\n').split(': ')[1]
            circles.append(circle)
        training_test.write(uid + ',' + str(len(circles)) + ',' + ';'.join(circles) + '\n')
training_test.close()

base = open("training_base1.csv", "w")
base.write('UserId,Predicted\n')
for uid in outs:
    file_handle = open("Data/egonets/{0}.egonet".format(uid))
    friends = []
    for line in file_handle:
        friends.append(line.split(":")[0])
    base.write(uid + ",1," + " ".join(friends) + '\n')
    file_handle.close()
base.close()
