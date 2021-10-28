function neighbours_intensity = get_26_neighbours(current_img, bottom_img, top_img, current_i, current_j)
% return 26 neighbours intensities
% todo: improve this function
[height width] = size(current_img);
neighbours_intensity = [];
if current_i > 1 && current_i < height && current_j > 1 && current_j < width
    intensity = current_img(current_i -1, current_j);
    neighbours_intensity = [neighbours_intensity intensity];
    
    intensity = bottom_img(current_i-1, current_j);
    neighbours_intensity = [neighbours_intensity intensity];
    
    intensity = top_img(current_i-1, current_j);
    neighbours_intensity = [neighbours_intensity intensity];  
    
    intensity = current_img(current_i -1, current_j-1);
    neighbours_intensity = [neighbours_intensity intensity];

    intensity = current_img(current_i -1, current_j+1);
    neighbours_intensity = [neighbours_intensity intensity];

    intensity = current_img(current_i, current_j-1);
    neighbours_intensity = [neighbours_intensity intensity];

    intensity = current_img(current_i, current_j+1);
    neighbours_intensity = [neighbours_intensity intensity];

    intensity = current_img(current_i+1, current_j-1);
    neighbours_intensity = [neighbours_intensity intensity];

    intensity = current_img(current_i+1, current_j);
    neighbours_intensity = [neighbours_intensity intensity];

    intensity = current_img(current_i+1, current_j+1);
    neighbours_intensity = [neighbours_intensity intensity];

    intensity = bottom_img(current_i-1, current_j-1);
    neighbours_intensity = [neighbours_intensity intensity];

    intensity = bottom_img(current_i-1, current_j+1);
    neighbours_intensity = [neighbours_intensity intensity];

    intensity = bottom_img(current_i, current_j-1);
    neighbours_intensity = [neighbours_intensity intensity];

    intensity = bottom_img(current_i, current_j);
    neighbours_intensity = [neighbours_intensity intensity];

    intensity = bottom_img(current_i, current_j+1);
    neighbours_intensity = [neighbours_intensity intensity];

    intensity = bottom_img(current_i+1, current_j);
    neighbours_intensity = [neighbours_intensity intensity];

    intensity = bottom_img(current_i+1, current_j+1);
    neighbours_intensity = [neighbours_intensity intensity];

    intensity = bottom_img(current_i+1, current_j-1);
    neighbours_intensity = [neighbours_intensity intensity];

    intensity = top_img(current_i-1, current_j-1);
    neighbours_intensity = [neighbours_intensity intensity];

    intensity = top_img(current_i-1, current_j+1);
    neighbours_intensity = [neighbours_intensity intensity];

    intensity = top_img(current_i, current_j-1);
    neighbours_intensity = [neighbours_intensity intensity];

    intensity = top_img(current_i, current_j);
    neighbours_intensity = [neighbours_intensity intensity];

    intensity = top_img(current_i, current_j+1);
    neighbours_intensity = [neighbours_intensity intensity];

    intensity = top_img(current_i+1, current_j);
    neighbours_intensity = [neighbours_intensity intensity];

    intensity = top_img(current_i+1, current_j+1);
    neighbours_intensity = [neighbours_intensity intensity];

    intensity = top_img(current_i+1, current_j-1);
    neighbours_intensity = [neighbours_intensity intensity];

end



end