import random


class ToTensor:
    def __call__(self, img, target):
        import torchvision.transforms.functional as F
        return F.to_tensor(img), target


class RandomHFlip:
    """Horizontal flip keeps class semantics for cracks/potholes; boxes are mirrored."""
    def __init__(self, p=0.5):
        self.p = p

    def __call__(self, img, target):
        if random.random() < self.p:
            img = img.flip(-1)
            w = img.shape[-1]
            b = target["boxes"].clone()
            b[:, 0] = w - target["boxes"][:, 2]
            b[:, 2] = w - target["boxes"][:, 0]
            target["boxes"] = b
        return img, target


class Compose:
    def __init__(self, ts):
        self.ts = ts

    def __call__(self, img, target):
        for t in self.ts:
            img, target = t(img, target)
        return img, target


def train_transforms():
    return Compose([ToTensor(), RandomHFlip()])


def eval_transforms():
    return Compose([ToTensor()])
