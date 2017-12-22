# Requirements: Anaconda

# For windows set the following environment variable
# LIBFREENECT2_INSTALL_PREFIX
# C:\Users\MiNdOs\Desktop\Master\Thesis\Kinect\libfreenect2
# Add the following to the PATH environment variable
# C:\Users\MiNdOs\Desktop\Master\Thesis\Kinect\libfreenect2\bin

# Adjust the location in environment.yml

# Go to the folder C:\Users\MiNdOs\Anaconda3\Scripts
conda env create -f environment.yml

# If cython fails activate the anaconda environment
pip install cython
# If cl.exe missing, launch Visual Studio installer and enable C++ development
