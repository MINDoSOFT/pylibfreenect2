bShow = true;
bSave = true;

sceneName = 'my_room';

outputDir = ['output' filesep sceneName filesep 'for_std2p'];
outImageDir = [outputDir filesep 'images'];
outRawDepthDir = [outputDir filesep 'rawdepth'];
outDepthDir = [outputDir filesep 'depth'];

exists_or_mkdir(outputDir);
exists_or_mkdir(outImageDir);
exists_or_mkdir(outRawDepthDir);
exists_or_mkdir(outDepthDir);

inputDir = ['output' filesep sceneName];

bigDepthDir = [inputDir filesep 'bigdepth'];
imageDir = [inputDir filesep 'images'];

filesImages = dir([imageDir filesep '*.png']);
filesImages(end) = [];
  
xlsfiles={filesImages.name};
filesImages=sort(xlsfiles);

filesBigDepths = dir([bigDepthDir filesep '*.png']);
filesBigDepths(end) = [];
  
xlsfiles={filesBigDepths.name};
filesBigDepths=sort(xlsfiles);

frameNum = 1;

for ii = 1 : numel(filesImages)
    sFrameNum = sprintf('%04d', frameNum);
    image = imread([imageDir filesep filesImages{ii}]);
    bigDepth = imread([bigDepthDir filesep filesBigDepths{ii}]);
    
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

    % Inpaint the raw depth
    alphaLevinEtAl = 1; % Like the default in fill_depth_colorization
    imgRgbNorm = imNormalize(image, 2);
    kinectV2MaxDepth = 4.5;
    % Convert big depth to meters
    bigDepthAdj = double(bigDepth) * (kinectV2MaxDepth / 255);
    imgDepthInpainted = fill_depth_colorization(imgRgbNorm, bigDepthAdj, alphaLevinEtAl);

    if bShow
        imshow(image);
        title('Image');
        figure;

        imshow(bigDepth);
        title('Raw depth');
        figure;

        imshow(imgDepthInpainted);
        title('Inpainted depth');
    end;

    if bSave
        imwrite(image, [outImageDir filesep 'img_' sFrameNum '.png']);
        imwrite(imgDepthInpainted, [outDepthDir filesep 'img_' sFrameNum '.png']);
        imwrite(bigDepth, [outRawDepthDir filesep 'img_' sFrameNum '.png']);
    end;
    
    frameNum = frameNum + 1;
end;