function scores = shi_tomasi(img, patch_size)

sobel_X = [-1, 0, 1; 
    -2, 0, 2;
    -1, 0, 1];

sobel_Y = [-1, -2, -1;
    0, 0, 0;
    1, 2, 1];

Ix = conv2(img, sobel_X, 'valid');
Iy = conv2(img, sobel_Y, 'valid');

Ix_square = immultiply(Ix, Ix);
Iy_square = immultiply(Iy, Iy);

Ixy = immultiply(Ix, Iy);

% calculate patches for each Ix, Iy, Ixy
patches_Ix_square = get_image_patches(Ix_square, patch_size);
patches_Iy_square = get_image_patches(Iy_square, patch_size);
patches_Ixy = get_image_patches(Ixy, patch_size);

[height, width] = size(patches_Ix_square);

% initialize score
scores = zeros(height, width);

for u=1:width
    for v=1:height
        sigma_Ix_square = sum(patches_Ix_square{v, u}, 'all'); 
        sigma_Iy_square = sum(patches_Iy_square{v, u}, 'all');
        sigma_Ixy_square = sum(patches_Ixy{v, u}, 'all');
        
        % calculate M matrix for each pixel
        M{v, u} = [sigma_Ix_square sigma_Ixy_square; sigma_Ixy_square sigma_Iy_square];
        
        % calculating eigen values
        eigen{v,u} = eig(M{v,u});
        scores(v, u) = max(eigen{v,u}(2), eigen{v,u}(1));
    end
end

% add padding to bring to same size as image
scores = padarray(scores, [ceil(patch_size/2) ceil(patch_size/2)], 0, 'both');

end
