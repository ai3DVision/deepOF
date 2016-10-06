"""Contains a warp flow model, which adapt from vgg16 net.
"""
import tensorflow as tf
import tensorflow.contrib.slim as slim

def deep3D(inputs, outputs, loss_weight, labels):
    """Creates the warp flow model.

    Args:
    inputs: 4D image tensor corresponding to prev frames
    outputs: 4D image tensor corresponding to next frames
    Returns:
    predicted next frames
    """

    with slim.arg_scope([slim.conv2d, slim.fully_connected], 
                        activation_fn=tf.nn.relu,
                        weights_initializer=tf.truncated_normal_initializer(0.0, 0.01),
                        weights_regularizer=slim.l2_regularizer(0.0005)):
        # with tf.device('/gpu:0'):
        # conv1_1 = slim.conv2d(inputs, 64, [3, 3], scope='conv1_1')
        conv1_1 = slim.conv2d(tf.concat(3, [inputs, outputs]), 64, [3, 3], scope='conv1_1')
        pool1 = slim.max_pool2d(conv1_1, [2, 2], scope='pool1')
        conv2_1 = slim.conv2d(pool1, 128, [3, 3], scope='conv2_1')
        pool2 = slim.max_pool2d(conv2_1, [2, 2], scope='pool2')
        conv3_1 = slim.conv2d(pool2, 256, [3, 3], scope='conv3_1')
        conv3_2 = slim.conv2d(conv3_1, 256, [3, 3], scope='conv3_2')
        pool3 = slim.max_pool2d(conv3_2, [2, 2], scope='pool3')
        conv4_1 = slim.conv2d(pool3, 512, [3, 3], scope='conv4_1')
        conv4_2 = slim.conv2d(conv4_1, 512, [3, 3], scope='conv4_2')
        pool4 = slim.max_pool2d(conv4_2, [2, 2], scope='pool4')
        conv5_1 = slim.conv2d(pool4, 512, [3, 3], scope='conv5_1')
        conv5_2 = slim.conv2d(conv5_1, 512, [3, 3], scope='conv5_2')
        pool5 = slim.max_pool2d(conv5_2, [2, 2], scope='pool5')
        flatten5 = slim.flatten(pool5, scope='flatten5')
        fc6 = slim.fully_connected(flatten5, 4096, scope='fc6')
        dropout6 = slim.dropout(fc6, 0.9, scope='dropout6')
        fc7 = slim.fully_connected(dropout6, 4096, scope='fc7')
        dropout7 = slim.dropout(fc7, 0.9, scope='dropout7')
        fc8 = slim.fully_connected(dropout7, 101, scope='fc8')
        logits = slim.fully_connected(fc8, 101, activation_fn=None, scope='logits')

        actionLoss = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(logits, labels))

        predictions = tf.nn.softmax(logits, name='predictions')
        # actionLoss = slim.losses.softmax_cross_entropy(predictions, tf.one_hot(labels, 101))

        zeroCon = tf.constant(0)
        losses = [zeroCon, zeroCon, zeroCon, zeroCon, zeroCon, zeroCon, actionLoss]
        flows_all = [zeroCon, zeroCon, zeroCon, zeroCon, zeroCon, zeroCon]

        slim.losses.add_loss(actionLoss)
        
        return losses, flows_all, predictions
        # channels = 40       # Maybe 60 later
        # reshape_h = pool4.get_shape()[1].value/2
        # reshape_w = pool4.get_shape()[2].value/2
     
        # fc8_flow = slim.fully_connected(dropout7, channels*reshape_h*reshape_w, scope='d5')
        # bn_pool1 = slim.batch_norm(pool1, scope='bn_pool1')
        # bn_pool2 = slim.batch_norm(pool2, scope='bn_pool2')
        # bn_pool3 = slim.batch_norm(pool3, scope='bn_pool3')
        # bn_pool4 = slim.batch_norm(pool4, scope='bn_pool4')

        # # Maybe try no batch norm
        # d1 = slim.conv2d(bn_pool1, channels, [3, 3], scope='d1')
        # d2 = slim.conv2d(bn_pool2, channels, [3, 3], scope='d2')
        # d3 = slim.conv2d(bn_pool3, channels, [3, 3], scope='d3')
        # d4 = slim.conv2d(bn_pool4, channels, [3, 3], scope='d4')
        # d5 = tf.reshape(fc8_flow, [-1, reshape_h, reshape_w, channels])

        # scale = 1
        # deconv_1 = slim.conv2d_transpose(d1, channels, [2*scale, 2*scale], stride=scale, scope='deconv_1')
        # scale *= 2
        # deconv_2 = slim.conv2d_transpose(d2, channels, [2*scale, 2*scale], stride=scale, scope='deconv_2')
        # scale *= 2
        # deconv_3 = slim.conv2d_transpose(d3, channels, [2*scale, 2*scale], stride=scale, scope='deconv_3')
        # scale *= 2
        # deconv_4 = slim.conv2d_transpose(d4, channels, [2*scale, 2*scale], stride=scale, scope='deconv_4')
        # scale *= 2
        # deconv_5 = slim.conv2d_transpose(d5, channels, [2*scale, 2*scale], stride=scale, scope='deconv_5')
        # flows = tf.add_n([deconv_1, deconv_2, deconv_3, deconv_4, deconv_5])

        # scale = 2
        # # Add multiple intermediate loss
        # # d1_up = slim.conv2d_transpose(d1, channels, [2*scale, 2*scale], stride=scale, scope='d1_up')
        # d1_flows = slim.conv2d(d1, 2, [3, 3], activation_fn=None, scope='d1_flows')
        # # d2_up = slim.conv2d_transpose(d2, channels, [2*scale, 2*scale], stride=scale, scope='d2_up')
        # d2_flows = slim.conv2d(d2, 2, [3, 3], activation_fn=None, scope='d2_flows')
        # # d3_up = slim.conv2d_transpose(d3, channels, [2*scale, 2*scale], stride=scale, scope='d3_up')
        # d3_flows = slim.conv2d(d3, 2, [3, 3], activation_fn=None, scope='d3_flows')
        # # d4_up = slim.conv2d_transpose(d4, channels, [2*scale, 2*scale], stride=scale, scope='d4_up')
        # d4_flows = slim.conv2d(d4, 2, [3, 3], activation_fn=None, scope='d4_flows')
        # # d5_up = slim.conv2d_transpose(d5, channels, [2*scale, 2*scale], stride=scale, scope='d5_up')
        # d5_flows = slim.conv2d(d5, 2, [3, 3], activation_fn=None, scope='d5_flows')

        # flows = slim.conv2d_transpose(flows, channels, [2*scale, 2*scale], stride=scale, scope='deconv_final')
        # flows = slim.conv2d(flows, 2, [3, 3], activation_fn=None, scope='final_conv')
            
        # epsilon = tf.constant(0.001, name='epsilon')
        # alpha_c = tf.constant(0.4, name='alpha_c')
        # alpha_s = tf.constant(0.3, name='alpha_s')
        # lambda_smooth = tf.constant(1.0, name='lambda_smooth')

        # d1_input = tf.image.resize_bilinear(inputs, [d1_flows.get_shape()[1].value, d1_flows.get_shape()[2].value])
        # d1_output = tf.image.resize_bilinear(outputs, [d1_flows.get_shape()[1].value, d1_flows.get_shape()[2].value])
        # d1_loss = loss_interp(d1_flows, d1_input, d1_output, epsilon, alpha_c, alpha_s, lambda_smooth)

        # d2_input = tf.image.resize_bilinear(inputs, [d2_flows.get_shape()[1].value, d2_flows.get_shape()[2].value])
        # d2_output = tf.image.resize_bilinear(outputs, [d2_flows.get_shape()[1].value, d2_flows.get_shape()[2].value])
        # d2_loss = loss_interp(d2_flows, d2_input, d2_output, epsilon, alpha_c, alpha_s, lambda_smooth)

        # d3_input = tf.image.resize_bilinear(inputs, [d3_flows.get_shape()[1].value, d3_flows.get_shape()[2].value])
        # d3_output = tf.image.resize_bilinear(outputs, [d3_flows.get_shape()[1].value, d3_flows.get_shape()[2].value])
        # d3_loss = loss_interp(d3_flows, d3_input, d3_output, epsilon, alpha_c, alpha_s, lambda_smooth)

        # d4_input = tf.image.resize_bilinear(inputs, [d4_flows.get_shape()[1].value, d4_flows.get_shape()[2].value])
        # d4_output = tf.image.resize_bilinear(outputs, [d4_flows.get_shape()[1].value, d4_flows.get_shape()[2].value])
        # d4_loss = loss_interp(d4_flows, d4_input, d4_output, epsilon, alpha_c, alpha_s, lambda_smooth)

        # d5_input = tf.image.resize_bilinear(inputs, [d5_flows.get_shape()[1].value, d5_flows.get_shape()[2].value])
        # d5_output = tf.image.resize_bilinear(outputs, [d5_flows.get_shape()[1].value, d5_flows.get_shape()[2].value])
        # d5_loss = loss_interp(d5_flows, d5_input, d5_output, epsilon, alpha_c, alpha_s, lambda_smooth)

        # final_loss = loss_interp(flows, inputs, outputs, epsilon, alpha_c, alpha_s, lambda_smooth)

        # loss_weight = [16,8,4,2,1,32]
        # all_loss = loss_weight[0]*d1_loss + loss_weight[1]*d2_loss + loss_weight[2]*d3_loss + loss_weight[3]*d4_loss + loss_weight[4]*d5_loss + loss_weight[5]*final_loss
        # # slim.losses.add_loss(all_loss)
        # slim.losses.add_loss(actionLoss)
        # losses = [d1_loss, d2_loss, d3_loss, d4_loss, d5_loss, final_loss, actionLoss]
        # flows_all = [flows, d1_flows, d2_flows, d3_flows, d4_flows, d5_flows]

        # # return losses, flows_all, tf.image.resize_bilinear(flows, [436, 1024])
        # return losses, flows_all, predictions
        # return losses, flows

def flowNet(inputs, outputs, loss_weight, labels):
    """Creates the warp flow model.

    Args:
    inputs: 4D image tensor corresponding to prev frames
    outputs: 4D image tensor corresponding to next frames
    Returns:
    predicted next frames
    """

    with slim.arg_scope([slim.conv2d, slim.fully_connected, slim.conv2d_transpose], 
                        activation_fn=tf.nn.relu,       # original use leaky ReLU
                        weights_initializer=tf.truncated_normal_initializer(0.0, 0.01),     # original use MSRA initializer
                        weights_regularizer=slim.l2_regularizer(0.0005)):
        # Contracting part
        conv1 = slim.conv2d(tf.concat(3, [inputs, outputs]), 64, [7, 7], stride=2, scope='conv1')
        conv2 = slim.conv2d(conv1, 128, [5, 5], stride=2, scope='conv2')
        conv3_1 = slim.conv2d(conv2, 256, [5, 5], stride=2, scope='conv3_1')
        conv3_2 = slim.conv2d(conv3_1, 256, [3, 3], scope='conv3_2')
        conv4_1 = slim.conv2d(conv3_2, 512, [3, 3], stride=2, scope='conv4_1')
        conv4_2 = slim.conv2d(conv4_1, 512, [3, 3], scope='conv4_2')
        conv5_1 = slim.conv2d(conv4_2, 512, [3, 3], stride=2, scope='conv5_1')
        conv5_2 = slim.conv2d(conv5_1, 512, [3, 3], scope='conv5_2')
        conv6_1 = slim.conv2d(conv5_2, 1024, [3, 3], stride=2, scope='conv6_1')
        conv6_2 = slim.conv2d(conv6_1, 1024, [3, 3], scope='conv6_2')

        # Action recognition
        flatten6 = slim.flatten(conv6_2, scope='flatten6')
        fc7 = slim.fully_connected(flatten6, 4096, scope='fc7')
        dropout7 = slim.dropout(fc7, 0.5, scope='dropout7')
        fc8 = slim.fully_connected(dropout7, 4096, scope='fc8')
        dropout8 = slim.dropout(fc8, 0.5, scope='dropout8') 
        logits = slim.fully_connected(dropout8, 101, activation_fn=None, scope='logits')
        predictions = tf.nn.softmax(logits, name='predictions')

        actionLoss = slim.losses.softmax_cross_entropy(predictions, tf.one_hot(labels, 101))

        # Hyper-params for computing unsupervised loss
        epsilon = tf.constant(0.001, name='epsilon')
        alpha_c = tf.constant(0.4, name='alpha_c')
        alpha_s = tf.constant(0.3, name='alpha_s')
        lambda_smooth = tf.constant(1.0, name='lambda_smooth')

        # Expanding part
        pr6 = slim.conv2d(conv6_2, 2, [3, 3], scope='pr6')
        h6 = pr6.get_shape()[1].value
        w6 = pr6.get_shape()[2].value
        pr6_input = tf.image.resize_bilinear(inputs, [h6, w6])
        pr6_output = tf.image.resize_bilinear(outputs, [h6, w6])
        loss6 = loss_interp(pr6, pr6_input, pr6_output, epsilon, alpha_c, alpha_s, lambda_smooth)
        scale = 2
        upconv5 = slim.conv2d_transpose(conv6_2, 512, [2*scale, 2*scale], stride=scale, scope='up_conv5')
        pr6to5 = slim.conv2d_transpose(pr6, 2, [2*scale, 2*scale], stride=scale, scope='up_pr6to5')
        concat5 = tf.concat(3, [upconv5, conv5_2, pr6to5])

        pr5 = slim.conv2d(concat5, 2, [3, 3], scope='pr5')
        h5 = pr5.get_shape()[1].value
        w5 = pr5.get_shape()[2].value
        pr5_input = tf.image.resize_bilinear(inputs, [h5, w5])
        pr5_output = tf.image.resize_bilinear(outputs, [h5, w5])
        loss5 = loss_interp(pr5, pr5_input, pr5_output, epsilon, alpha_c, alpha_s, lambda_smooth)
        upconv4 = slim.conv2d_transpose(concat5, 256, [2*scale, 2*scale], stride=scale, scope='up_conv4')
        pr5to4 = slim.conv2d_transpose(pr5, 2, [2*scale, 2*scale], stride=scale, scope='up_pr5to4')
        concat4 = tf.concat(3, [upconv4, conv4_2, pr5to4])

        pr4 = slim.conv2d(concat4, 2, [3, 3], scope='pr4')
        h4 = pr4.get_shape()[1].value
        w4 = pr4.get_shape()[2].value
        pr4_input = tf.image.resize_bilinear(inputs, [h4, w4])
        pr4_output = tf.image.resize_bilinear(outputs, [h4, w4])
        loss4 = loss_interp(pr4, pr4_input, pr4_output, epsilon, alpha_c, alpha_s, lambda_smooth)
        upconv3 = slim.conv2d_transpose(concat4, 128, [2*scale, 2*scale], stride=scale, scope='up_conv3')
        pr4to3 = slim.conv2d_transpose(pr4, 2, [2*scale, 2*scale], stride=scale, scope='up_pr4to3')
        concat3 = tf.concat(3, [upconv3, conv3_2, pr4to3])

        pr3 = slim.conv2d(concat3, 2, [3, 3], scope='pr3')
        h3 = pr3.get_shape()[1].value
        w3 = pr3.get_shape()[2].value
        pr3_input = tf.image.resize_bilinear(inputs, [h3, w3])
        pr3_output = tf.image.resize_bilinear(outputs, [h3, w3])
        loss3 = loss_interp(pr3, pr3_input, pr3_output, epsilon, alpha_c, alpha_s, lambda_smooth)
        upconv2 = slim.conv2d_transpose(concat3, 128, [2*scale, 2*scale], stride=scale, scope='up_conv2')
        pr3to2 = slim.conv2d_transpose(pr3, 2, [2*scale, 2*scale], stride=scale, scope='up_pr3to2')
        concat2 = tf.concat(3, [upconv2, conv2, pr3to2])

        pr2 = slim.conv2d(concat2, 2, [3, 3], scope='pr2')
        h2 = pr2.get_shape()[1].value
        w2 = pr2.get_shape()[2].value
        pr2_input = tf.image.resize_bilinear(inputs, [h2, w2])
        pr2_output = tf.image.resize_bilinear(outputs, [h2, w2])
        loss2 = loss_interp(pr2, pr2_input, pr2_output, epsilon, alpha_c, alpha_s, lambda_smooth)
        upconv1 = slim.conv2d_transpose(concat2, 256, [2*scale, 2*scale], stride=scale, scope='up_conv1')
        pr2to1 = slim.conv2d_transpose(pr2, 2, [2*scale, 2*scale], stride=scale, scope='up_pr2to1')
        concat1 = tf.concat(3, [upconv1, conv1, pr2to1])

        pr1 = slim.conv2d(concat1, 2, [3, 3], scope='pr1')
        h1 = pr1.get_shape()[1].value
        w1 = pr1.get_shape()[2].value
        pr1_input = tf.image.resize_bilinear(inputs, [h1, w1])
        pr1_output = tf.image.resize_bilinear(outputs, [h1, w1])
        loss1 = loss_interp(pr1, pr1_input, pr1_output, epsilon, alpha_c, alpha_s, lambda_smooth)
        
        all_loss = loss_weight[0]*loss1 + loss_weight[1]*loss2 + loss_weight[2]*loss3 + loss_weight[3]*loss4 + loss_weight[4]*loss5 + loss_weight[5]*loss6
        slim.losses.add_loss(all_loss)
        losses = [loss1, loss2, loss3, loss4, loss5, loss6, actionLoss]
        # pr1 = tf.mul(tf.constant(20.0), pr1)
        flows_all = [pr1, pr2, pr3, pr4, pr5, pr6]

        return losses, flows_all, predictions

def loss_interp(flows, inputs, outputs, epsilon, alpha_c, alpha_s, lambda_smooth):

    shape = inputs.get_shape()
    shape = [int(dim) for dim in shape]
    inputs_flat = tf.reshape(inputs, [shape[0], -1, shape[3]])
    outputs_flat = tf.reshape(outputs, [shape[0], -1, shape[3]])

    flows = tf.reshape(flows, [shape[0], -1, 2])
    floor_flows = tf.to_int32(tf.floor(flows))
    weights_flows = flows - tf.floor(flows)

    pos_x = tf.range(shape[1])
    pos_x = tf.tile(tf.expand_dims(pos_x, 1), [1, shape[2]])
    pos_x = tf.reshape(pos_x, [-1])
    pos_y = tf.range(shape[2])
    pos_y = tf.tile(tf.expand_dims(pos_y, 0), [shape[1], 1])
    pos_y = tf.reshape(pos_y, [-1])


    batch, batch_1 = [], []
    for b in range(shape[0]):
        channel, channel_1 = [], []
        for c in range(shape[3]):
            # predicted positions
            pos1 = (pos_x + floor_flows[b, :, 0])*shape[2] + (pos_y + floor_flows[b, :, 1] )
            pos2 = (pos_x + floor_flows[b, :, 0] + 1)*shape[2] + (pos_y + floor_flows[b, :, 1] )
            pos3 = (pos_x + floor_flows[b, :, 0])*shape[2] + (pos_y + floor_flows[b, :, 1] + 1)
            pos4 = (pos_x + floor_flows[b, :, 0] + 1)*shape[2] + (pos_y + floor_flows[b, :, 1] + 1)
            pos5 = (pos_x - floor_flows[b, :, 0])*shape[2] + (pos_y - floor_flows[b, :, 1] )
            pos6 = (pos_x - floor_flows[b, :, 0] - 1)*shape[2] + (pos_y - floor_flows[b, :, 1] )
            pos7 = (pos_x - floor_flows[b, :, 0])*shape[2] + (pos_y - floor_flows[b, :, 1] - 1)
            pos8 = (pos_x - floor_flows[b, :, 0] - 1)*shape[2] + (pos_y - floor_flows[b, :, 1] - 1)

            zero = tf.zeros([], dtype='int32')
            pos1 = tf.clip_by_value(pos1, zero, shape[1]*shape[2])
            pos2 = tf.clip_by_value(pos2, zero, shape[1]*shape[2])
            pos3 = tf.clip_by_value(pos3, zero, shape[1]*shape[2])
            pos4 = tf.clip_by_value(pos4, zero, shape[1]*shape[2])
            pos5 = tf.clip_by_value(pos5, zero, shape[1]*shape[2])
            pos6 = tf.clip_by_value(pos6, zero, shape[1]*shape[2])
            pos7 = tf.clip_by_value(pos7, zero, shape[1]*shape[2])
            pos8 = tf.clip_by_value(pos8, zero, shape[1]*shape[2])

            # get the corresponding pixels
            pixel1 = tf.gather(inputs_flat[b, :, c], pos1)
            pixel2 = tf.gather(inputs_flat[b, :, c], pos2)
            pixel3 = tf.gather(inputs_flat[b, :, c], pos3)
            pixel4 = tf.gather(inputs_flat[b, :, c], pos4)
            pixel5 = tf.gather(outputs_flat[b, :, c], pos5)
            pixel6 = tf.gather(outputs_flat[b, :, c], pos6)
            pixel7 = tf.gather(outputs_flat[b, :, c], pos7)
            pixel8 = tf.gather(outputs_flat[b, :, c], pos8)

            # linear interpretation of these predicted pixels
            xw = weights_flows[b, :, 0]
            yw = weights_flows[b, :, 1]
            img = tf.mul(pixel1, (1-xw)*(1-yw)) + tf.mul(pixel2, xw*(1-yw)) + \
                      tf.mul(pixel3, (1-xw)*yw) + tf.mul(pixel4, xw*yw)
            img_1 = tf.mul(pixel5, (1-xw)*(1-yw)) + tf.mul(pixel6, xw*(1-yw)) + \
                      tf.mul(pixel7, (1-xw)*yw) + tf.mul(pixel8, xw*yw)
            channel.append(img)
            channel_1.append(img_1)
        batch.append(tf.transpose(tf.pack(channel)))
        batch_1.append(tf.transpose(tf.pack(channel_1)))
    preds = tf.pack(batch)
    reconstructs = tf.pack(batch_1)
    
    loss_predict = tf.contrib.losses.sum_of_squares(preds, outputs_flat)
    loss_reconstruct = tf.contrib.losses.sum_of_squares(reconstructs, inputs_flat)
    # slim.losses.add_loss(tf.minimum(loss_predict, loss_reconstruct))

    # Charbonnier penalty function
    loss_min = tf.minimum(loss_predict, loss_reconstruct)
    Charbonnier = tf.pow(loss_min + tf.square(epsilon), alpha_c)

    # Smoothness loss
    flow_vis = tf.reshape(flows,[shape[0], shape[1], shape[2], 2])
    flowx = flow_vis[:,:,:,0]
    flowy = flow_vis[:,:,:,1]
    a = tf.reduce_mean(tf.pow(tf.square(tf.sub(flowx[:, :-1, :], flowx[:, 1:, :])) + tf.square(epsilon), alpha_s))          # u(i,j) - u(i+1,j)
    b = tf.reduce_mean(tf.pow(tf.square(tf.sub(flowx[:, :, :-1], flowx[:, :, 1:])) + tf.square(epsilon), alpha_s))          # u(i,j) - u(i,j+1)
    c = tf.reduce_mean(tf.pow(tf.square(tf.sub(flowy[:, :-1, :], flowy[:, 1:, :])) + tf.square(epsilon), alpha_s))          # v(i,j) - v(i+1,j)
    d = tf.reduce_mean(tf.pow(tf.square(tf.sub(flowy[:, :, :-1], flowy[:, :, 1:])) + tf.square(epsilon), alpha_s))          # v(i,j) - v(i,j+1)
    loss_smooth = tf.add_n([a, b, c, d])

    return Charbonnier + lambda_smooth * loss_smooth



