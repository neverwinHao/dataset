import cv2
import numpy as np

def find_lane_pixels(binary_warped, nwindows, margin, minpix):
    histogram = list(binary_warped[-10, :])
    leftx_base = margin // 2
    rightx_base = 320 - margin // 2
    out_img = np.dstack((binary_warped, binary_warped, binary_warped))
    sum = 0
    count = 0
    flag_left = 0
    flag_right = 0
    line_left = []
    line_right = []
    for i in range(160):
        if histogram[i] == 255:
            sum += i
            count += 1
    if count != 0:
        leftx_base = sum // count
        flag_left = 1
    elif count == 0:
        leftx_base = 1
    sum = 0
    count = 0
    for i in range(161, 320):
        if histogram[i] == 255:
            sum += i
            count += 1
    if count != 0:
        rightx_base = sum // count
        flag_right = 1
    elif count == 0:
        rightx_base = 319

    summ = flag_right + flag_left
    # print("left",flag_left)
    # print("right",flag_right)
    if abs(leftx_base - rightx_base) <= 20:
        summ = 1
    window_height = np.int(binary_warped.shape[0] // nwindows)
    # Identify the x and y positions of all nonzero pixels in the image
    nonzero = binary_warped.nonzero()
    nonzeroy = np.array(nonzero[0])
    nonzerox = np.array(nonzero[1])
    if summ == 1:
        if (flag_left == 0):
            current = rightx_base
        else:
            current = leftx_base
        lane_inds = []
        line = []
        # Step through the windows one by one
        for window in range(nwindows):
            win_y_low = binary_warped.shape[0] - (window + 1) * window_height
            win_y_high = binary_warped.shape[0] - window * window_height
            win_low = current - margin
            win_high = current + margin
            line.append(current)
            cv2.rectangle(out_img, (win_low, win_y_low),
                          (win_high, win_y_high), (0, 255, 0), 2)
            good_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
                         (nonzerox >= win_low) & (nonzerox < win_high)).nonzero()[0]
            lane_inds.append(good_inds)
            if len(good_inds) > minpix:
                current = np.int(np.mean(nonzerox[good_inds]))

        if (line[15] > line[0]):
            line_left = line
            left_lane_inds = lane_inds
            line_right = 0
            current = 319
        else:
            line_right = line
            right_lane_inds = lane_inds
            line_left = 0
            current = 1
        lane_inds = []
        line = []
        for window in range(nwindows):
            win_y_low = binary_warped.shape[0] - (window + 1) * window_height
            win_y_high = binary_warped.shape[0] - window * window_height
            win_low = current - margin
            win_high = current + margin
            line.append(current)
            cv2.rectangle(out_img, (win_low, win_y_low),
                          (win_high, win_y_high), (0, 255, 0), 2)
            good_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
                         (nonzerox >= win_low) & (nonzerox < win_high)).nonzero()[0]
            # good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
            #                    (nonzerox >= win_xright_low) & (nonzerox < win_xright_high)).nonzero()[0]

            # Append these indices to the lists
            lane_inds.append(good_inds)
            # right_lane_inds.append(good_right_inds)

            # If you found > minpix pixels, recenter next window on their mean position
            if len(good_inds) > minpix:
                current = np.int(np.mean(nonzerox[good_inds]))
        if (line_right == 0):
            line_right = line
            right_lane_inds = lane_inds
        else:
            line_left = line
            left_lane_inds = lane_inds

    else:
        if ((flag_left + flag_right) == 0):
            leftx_base = 1
            rightx_base = 319
        leftx_current = leftx_base
        rightx_current = rightx_base

        # Create empty lists to receive left and right lane pixel indices
        left_lane_inds = []
        right_lane_inds = []

        # Step through the windows one by one
        for window in range(nwindows):
            # Identify window boundaries in x and y (and right and left)
            win_y_low = binary_warped.shape[0] - (window + 1) * window_height
            win_y_high = binary_warped.shape[0] - window * window_height
            win_xleft_low = leftx_current - margin
            win_xleft_high = leftx_current + margin
            win_xright_low = rightx_current - margin
            win_xright_high = rightx_current + margin
            line_left.append(leftx_current)
            line_right.append(rightx_current)
            # Draw the windows on the visualization image
            cv2.rectangle(out_img, (win_xleft_low, win_y_low),
                          (win_xleft_high, win_y_high), (0, 255, 0), 2)
            cv2.rectangle(out_img, (win_xright_low, win_y_low),
                          (win_xright_high, win_y_high), (0, 255, 0), 2)

            # Identify the nonzero pixels in x and y within the window #
            good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
                              (nonzerox >= win_xleft_low) & (nonzerox < win_xleft_high)).nonzero()[0]
            good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
                               (nonzerox >= win_xright_low) & (nonzerox < win_xright_high)).nonzero()[0]

            # Append these indices to the lists
            left_lane_inds.append(good_left_inds)
            right_lane_inds.append(good_right_inds)

            # If you found > minpix pixels, recenter next window on their mean position
            if len(good_left_inds) > minpix:
                leftx_current = np.int(np.mean(nonzerox[good_left_inds]))
            if len(good_right_inds) > minpix:
                rightx_current = np.int(np.mean(nonzerox[good_right_inds]))

    middle = 0
    begin = 20
    for i in range(begin):
        middle += (line_left[i] + line_right[i])

    print("middle", middle / (2 * begin))
    # Concatenate the arrays of indices (previously was a list of lists of pixels)
    try:
        left_lane_inds = np.concatenate(left_lane_inds)
        right_lane_inds = np.concatenate(right_lane_inds)
    except ValueError:
        # Avoids an error if the above is not implemented fully
        pass
    # middle = (np.sum(left_lane_inds)+np.sum(right_lane_inds))/2*len(left_lane_inds)
    # print("aaa",middle)

    # Extract left and right line pixel positions
    leftx = nonzerox[left_lane_inds]
    lefty = nonzeroy[left_lane_inds]
    rightx = nonzerox[right_lane_inds]
    righty = nonzeroy[right_lane_inds]
    out_img[lefty, leftx] = [255, 0, 0]
    out_img[righty, rightx] = [0, 0, 255]
    return out_img

cap = cv2.VideoCapture(2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 400)  # 实际宽度是320
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 250)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FPS, 30)
count = 0  # 图片计数器

while (cap.isOpened()):
    ret, frame = cap.read()
    image = frame
    # image[0:110, :] = 0
    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # canny = cv2.Canny(blurred, 50, 150)
    # image = canny
    cv2.imshow('Result', image)
    cv2.imwrite(f'blue{count}.jpg', image)
    count += 1
    image[0:110, :] = 0
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    canny = cv2.Canny(blurred, 50, 150)
    kernel = np.ones((5, 5), np.uint8)
    dilated = cv2.dilate(canny, kernel, iterations=1)
    out_img = find_lane_pixels(dilated, nwindows=50, margin=20, minpix=20)
    k = cv2.waitKey(1)
    if k & 0x00FF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()