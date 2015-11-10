import numpy as np
import matplotlib.pyplot as plt
from sys import argv
from collections import defaultdict

if __name__ == "__main__":

	'''
	read in losses for l users, where the loss file is of the formaat:
	USER_ID_1: LOSS_1, LOSS_2, ..., LOSS_n_1
	USER_ID_2: LOSS_1, LOSS_2, ..., LOSS_n_2
	...
	USER_ID_l: LOSS_1, LOSS_2, ..., LOSS_n_l

	'''

	#define plotting constants
	col_end = np.array([1.0,0.0,0.0])
	col_start =  np.array([0.0,0.0,1.0])
	lw = 2 #line width
	ms = 10 #marker size
	fs = 14 #font size
	fs_labels = 12 #font size



	#o loss file...
	loss_files = argv[1:];
	colors = 'krmbc'

	l_idx = 1;
	losses = defaultdict(list)
	for loss_file in loss_files:

		loss_handle =  open(loss_file);

		# #get number of users...
		# num_users = 0
		# for line in loss_handle:
		# 	num_users += 1
		# num_users = float(num_users)


		loss_handle.close()
		loss_handle =  open(loss_file);

		#loop through each line in loss file (i.e., each user) and get loss of ALL best level splits as DICTIONARY...
		i=0;
		for line in loss_handle:
			line_split = line.strip().split(': ')
			uid = line_split[0]
			losses[uid].append(float(line_split[1])*100.0)
			i=i+1

	#print "" + len(losses.keys())
	num_users = len(losses.keys())
	i = 0
	for uid,loss_list in losses.iteritems():

		#calculate color of plotted line (blended from red-->blue)...
		f = loss_list[0]/45;
		col = tuple((1-f)*col_start + f*col_end)

		# if (num_users > 1):
		# 	f = (i)/(num_users - 1.0)
		# 	col = tuple((1-f)*col_start + f*col_end)
		# else:
		# 	col = (1,0,0)

		#plot losses of user...
		num_levels = len(loss_list)
		plot_lines = plt.plot(range(1,num_levels+1),loss_list)
		plt.setp(plot_lines,'color',col,'linewidth',lw,'marker','.','markersize',7)
		i=i+1


		# #loop through each line in loss file (i.e., each user) and get loss of ALL best level splits...
		# i=0;
		# losses = defaultdict(list)
		# users = np.zeros(num_users);
		# for line in loss_handle:
		# 	if (num_users > 1):
		# 		f = (i)/(num_users - 1.0);
		# 		col = tuple((1-f)*col_start + f*col_end)
		# 	else:
		# 		col = (1,0,0)

		# 	losses = [float(loss) for loss in line.strip().split(': ')[1].split(' ')]
		# 	num_levels = len(losses);
		# 	plot_lines = plt.plot(l_idx,losses)
		# 	plt.setp(plot_lines,'color',col,'linewidth',lw,'marker','.','markersize',7)
		# 	i+= 1


		#loop through each line in loss file (i.e., each user) and get loss of SINGLE best level split...
		# i=0;
		# losses = np.zeros(num_users);
		# users = np.zeros(num_users);
		# for line in loss_handle:
		# 	line_split = line.strip().split(': ')
		# 	users[i] = line_split[0]
		# 	losses[i] = float(line_split[1])*100.0
		# 	i=i+1
		# plot_lines = plt.plot(users,losses)
		# plt.setp(plot_lines,'color',colors[l_idx],'linewidth',lw,'linestyle','.','marker','.','markersize',ms)
		l_idx += 1;

	#finish plotting...
	plt.title('Training Set Error per User', fontsize=fs)
	plt.xlabel('Best Dendrogram Levels (descending)', fontsize=fs_labels)
	plt.ylabel('Normalized Error (%)', fontsize=fs_labels)
	plt.axis([.8,9.2,0,60])
	plt.xticks([1,2,3,4,5,6,7,8,9])
	plt.show();





	# #loop through each line in loss file (i.e., each user) and get loss of ALL best  level splits...
	# i=0;
	# losses = np.zeros(num_users);
	# users = np.zeros(num_users);
	# for line in loss_handle:
	# 	f = (i)/(num_users - 1.0);
	# 	col = tuple((1-f)*col_start + f*col_end)
	# 	losses = [float(loss) for loss in line.strip().split(': ')[1].split(' ')]
	# 	num_levels = len(losses);
	# 	plot = plt.plot(range(num_levels),losses)
	# 	plt.setp(lines,'color',col,'linewidth',lw,'marker','.','markersize',7)
	# 	i+= 1







