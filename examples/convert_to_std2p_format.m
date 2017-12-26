bigDepth = imread(['output' filesep 'my_room' filesep 'bigdepth' filesep 'img_0000.png']);

bdCenterX = size(bigDepth, 1) / 2;
bdCenterY = size(bigDepth, 2) / 2;


% These do not work with bigdepth, it gives not aligned depth with rgb
windowSizeX = 640;
windowSizeY = 480;

% (512, 424)
%windowSizeX = 512;
%windowSizeY = 424;

% To compensate for MATLAB row-wise style
temp = windowSizeX
windowSizeX = windowSizeY;
windowSizeY = temp;

% Crop a window from big depth
bdWindow = bigDepth(bdCenterX-(windowSizeX/2):bdCenterX+(windowSizeX/2)-1,bdCenterY-(windowSizeY/2):bdCenterY+(windowSizeY/2)-1);

image = imread(['output' filesep 'my_room' filesep 'images' filesep 'img_0000.png']);

imCenterX = size(image, 1) / 2;
imCenterY = size(image, 2) / 2;

% Crop same window from rgb image
imWindow = image(imCenterX-(windowSizeX/2):imCenterX+(windowSizeX/2)-1,imCenterY-(windowSizeY/2):imCenterY+(windowSizeY/2)-1);

undistoredDepth = imread(['output' filesep 'my_room' filesep 'undistored' filesep 'img_0000.png']);

imshow(image);
title('Image');
figure;

imshow(bigDepth);
title('Big depth');
figure;

imshow(bdWindow);
title('Big depth window');
figure;

imshow(imWindow);
title('Image window');
figure;

imshow(undistoredDepth);
title('Undistored depth');