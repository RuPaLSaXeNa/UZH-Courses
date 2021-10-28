clear all
close all
clc

num_scales = 3; % Scales per octave.
num_octaves = 5; % Number of octaves.
sigma = 1.6;
contrast_threshold = 0.04;
image_file_1 = 'images/img_1.jpg';
image_file_2 = 'images/img_2.jpg';
rescale_factor = 0.2; % Rescaling of the original image for speed.

images = {getImage(image_file_1, rescale_factor),...
    getImage(image_file_2, rescale_factor)};

kpt_locations = cell(1, 2);
descriptors = cell(1, 2);


for img_idx = 1:2
    img = images{img_idx};
    for octave_num = 1:num_octaves
        % getting guassian pyramid
        for s = -1:num_scales+1
            new_sigma = (2  .^ (s/num_scales)) * sigma;
            gauss = fspecial('gaussian', round([10*new_sigma*(2^num_octaves), 10*new_sigma*(2^num_octaves)]), new_sigma);
            filtered_img = imfilter(img, gauss, 'replicate', 'same');
            gaussian_pyramid{(s+2)+(6 * (octave_num -1))} = filtered_img;
        end
        % getting DoG pyramid
        for index = 1+(6 * (octave_num -1)):num_scales+3+(6 * (octave_num -1))
            if rem(index, 6) == 0
                break
            end
            DoG = gaussian_pyramid{index+1} - gaussian_pyramid{index};
            % suppress all points smaller than contrast threhold
            DoG_pyramid{index} = DoG.*(DoG>contrast_threshold);
        end
        img = downsample_img(images{img_idx}, 1/(2 .^ (octave_num)));
    end
    
    % Locate keypoints in scale and space
    choosen_octaves = [];
    choosen_scales = [];
    for octave_num = 1:num_octaves
        scale = 1;
        for index = 2+(6 * (octave_num -1)): num_scales+1+(6 * (octave_num -1))
            current_img = DoG_pyramid{index};
            bottom_img = DoG_pyramid{index - 1};
            top_img = DoG_pyramid{index + 1};
            [nonzero_i, nonzero_j] = find(current_img);
            for nonzero_index = 1:length(nonzero_i)
                current_pixel = current_img(nonzero_i(nonzero_index), nonzero_j(nonzero_index));
                neighbours = get_26_neighbours(current_img, bottom_img, top_img, nonzero_i(nonzero_index), nonzero_j(nonzero_index));
                max_neighbour = max(neighbours);
                if current_pixel < max_neighbour
                    DoG_pyramid{index}(nonzero_i(nonzero_index), nonzero_j(nonzero_index)) = 0;
                end
            end
            [nonzero_i_test, nonzero_j_test] = find(DoG_pyramid{index}>0);
            
            if length(nonzero_i_test) > 0 
                choosen_octaves = [choosen_octaves octave_num];
                choosen_scales = [choosen_scales scale];
            end
            scale = scale + 1;
            
            % taking only DoG images which has some keypoints detected
            nms_DoG_pyramid{index} = DoG_pyramid{index}.*(DoG_pyramid{index}>0);
            %nms_DoG_pyramid{index} = DoG_pyramid{index}
            
        end
    end
    
end

%{  

Write code to compute:
1)    image pyramid. Number of images in the pyarmid equals
      'num_octaves'.
2)    blurred images for each octave. Each octave contains
      'num_scales + 3' blurred images.
3)    'num_scales + 2' difference of Gaussians for each octave.
4)    Compute the keypoints with non-maximum suppression and
      discard candidates with the contrast threshold.
5)    Given the blurred images and keypoints, compute the
      descriptors. Discard keypoints/descriptors that are too close
      to the boundary of the image. Hence, you will most likely
      lose some keypoints that you have computed earlier.
%}

          
 

% Finally, match the descriptors using the function 'matchFeatures' and
% visualize the matches with the function 'showMatchedFeatures'.
% If you want, you can also implement the matching procedure yourself using
% 'knnsearch'.