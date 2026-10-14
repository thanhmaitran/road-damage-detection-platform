def build_detector(num_classes: int, pretrained=True, min_size=640, max_size=1066):
    """Faster R-CNN ResNet50-FPN with a new box head. num_classes excludes background."""
    import torchvision
    from torchvision.models.detection import FasterRCNN_ResNet50_FPN_Weights
    from torchvision.models.detection.faster_rcnn import FastRCNNPredictor

    weights = FasterRCNN_ResNet50_FPN_Weights.DEFAULT if pretrained else None
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(
        weights=weights, weights_backbone=None, min_size=min_size, max_size=max_size)
    in_f = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_f, num_classes + 1)
    return model
