function [points, intensities] = disparityToPointCloud(...
    disp_img, K, baseline, left_img)
% points should be 3xN and intensities 1xN, where N is the amount of pixels
% which have a valid disparity. I.e., only return points and intensities
% for pixels of left_img which have a valid disparity estimate! The i-th
% intensity should correspond to the i-th point.

K_inv = inv(K);

% get rows, col when there is a valid disparity
idxs = find(disp_img>0);
[rows, columns] = ind2sub(size(disp_img), idxs);

% get number of points with valid disparity
N = length(rows);

% initialize points and intensities
points = zeros(3,N);
intensities = zeros(1,N);

for i=1:N
    row = rows(i);
    col = columns(i);
    
    p0 = [col;row];
    
    disparity = disp_img(row, col);
    
    p1 = [col-disparity;row];
    
    k_inv_p0 = K_inv * [p0;1];
    k_inv_p1 = K_inv * [p1;1];
    A = [k_inv_p0, -k_inv_p1];
    A_transpose_A = transpose(A)*A;
    A_transpose_b = transpose(A)*[baseline;0;0];
    
    lambda = inv(A_transpose_A) * A_transpose_b;
    lambda_0 = lambda(1);
    
    points(:,i) = lambda_0 * K_inv * [p0;1];
    intensities(1,i) = left_img(row,col);

end
end
