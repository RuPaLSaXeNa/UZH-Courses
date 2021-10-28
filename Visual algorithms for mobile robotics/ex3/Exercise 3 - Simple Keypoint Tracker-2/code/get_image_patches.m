function patches = get_image_patches(img, patch_size)
imSz = size(img);

xIdxs = [floor(patch_size/2):1:(imSz(2)-floor(patch_size/2))];
yIdxs = [floor(patch_size/2):1:(imSz(1)-floor(patch_size/2))];

patches = cell(length(yIdxs)-1,length(xIdxs)-1);
for i = 1:length(yIdxs)-1
    Isub = img(yIdxs(i):yIdxs(i+1)-1,:,:);
    for j = 1:length(xIdxs)-1
        patches{i,j} = Isub(:,xIdxs(j):xIdxs(j+1)-1,:);
    end
end
end