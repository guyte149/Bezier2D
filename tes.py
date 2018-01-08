from h import *
import matplotlib.pyplot as plt
l_list = V2L([Vector2D(0,0), Vector2D(1,1), Vector2D(2,0.5)])
c1 = plt.Circle((1, 1), 1, fill=False)
fig, ax = plt.subplots()
ax.add_artist(c1)
plt.show()
