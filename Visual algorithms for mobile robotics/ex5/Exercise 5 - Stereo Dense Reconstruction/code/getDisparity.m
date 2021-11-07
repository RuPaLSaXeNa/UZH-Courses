function disp_img = getDisparity(...
    left_img, right_img, patch_radius, min_disp, max_disp)

    % left_img and right_img are both H x W and you should return a H x W
    % matrix containing the disparity d for each pixel of left_img. Set
    % disp_img to 0 for pixels where the SSD and/or d is not defined, and for d
    % estimates rejected in Part 2. patch_radius specifies the SSD patch and
    % each valid d should satisfy min_disp <= d <= max_disp.
    
    [height, width] = size(left_img);
    disp_img = zeros(height, width);
    
    patch_start_col = patch_radius + 1;
    patch_end_col = width - patch_radius;
    patch_end_row = height - patch_radius;
    
    patch_size = 2*patch_radius + 1;
    min_candidates = 2;
    
    parfor v = patch_start_col:patch_end_row
        start_compare_patch = v-patch_radius;
        end_compare_patch = v+patch_radius;
        
        for u = patch_start_col:patch_end_col
           if u-max_disp > patch_radius
               start_compare_patch_col = u-patch_radius;
               end_compare_patch_col = u+patch_radius;
               
               compare_patch = reshape((left_img(start_compare_patch:end_compare_patch, start_compare_patch_col:end_compare_patch_col)), 1, []);
               
               strip = inf(patch_size*patch_size, max_disp - min_disp - 1);
               strip(:,u:end) = 0;
               
               for patch_index = u-max_disp+1:u-min_disp-1
                   % assumed that sizes of both images are same
                   sliding_patch = reshape(right_img(start_compare_patch:end_compare_patch, patch_index-patch_radius:patch_index+patch_radius), 1, []);
                   strip(:, u - patch_index) = reshape(sliding_patch, [], 1);      
               end  
               strip = single(strip)';
               
               dist = pdist2(single(compare_patch), strip, 'squaredeuclidean');
               [sorted_dist, indices] = sort(dist);
               
               disparity = indices(1);
               
               min_dist = sorted_dist(1);
               threshold = 1.5*min_dist;
               hasoutliers = (sum(sorted_dist<threshold) > min_candidates);
               
               if (hasoutliers || disparity < min_disp || disparity > max_disp)
                   disparity = 0;
               end
               
               disp_img(v,u) = disparity;
           end
        end
    end
end
