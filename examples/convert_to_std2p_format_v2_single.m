bigDepth = imread(['output' filesep 'my_room' filesep 'bigdepth' filesep 'img_0000.png']);

bdCenterX = size(bigDepth, 1) / 2;
bdCenterY = size(bigDepth, 2) / 2;

image = imread(['output' filesep 'my_room' filesep 'images' filesep 'img_0000.png']);

imCenterX = size(image, 1) / 2;
imCenterY = size(image, 2) / 2;

windowSizeX = 640;
windowSizeY = 480;

% To compensate for MATLAB row-wise style
temp = windowSizeX
windowSizeX = windowSizeY;
windowSizeY = temp;

% Skip the top and bottom line of bigdepth so size is the same as rgb image
bigDepth = bigDepth(2:end-1, :);

% Crop the black (left and right) borders from bigdepth and from rgb image
% 320 from each side so the resize is done with integer number
cropSizeX = 320;
cropSizeY = 60;

bigDepth = bigDepth(cropSizeY+1:end-cropSizeY, cropSizeX+1:end-cropSizeX);
image = image(cropSizeY+1:end-cropSizeY, cropSizeX+1:end-cropSizeX, :);

% Resize image and bigdepth to window
scaleFactor = 0.5;

bigDepth = imresize(bigDepth, scaleFactor);
image = imresize(image, scaleFactor);

imshow(image);
title('Image');
figure;

imshow(bigDepth);
title('Big depth');