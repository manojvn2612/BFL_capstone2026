import torch
import segmentation_models_pytorch as smp
import numpy as np
import cv2
import matplotlib.pyplot as plt
class hr_net_inference:
    def __init__(self):
        # self.image_input = image_input
        self.NUM_CLASSES = 8
        self.CLASS_NAMES = ['Cutter', 'Fingerprint', 'Ink', 'Jig', 'Machining', 'Overcut', 'Pocket', 'Scratches']
        self.COLORS = [
                (255, 0, 0),    # Cutter
                (0, 255, 0),    # Fingerprint
                (0, 0, 255),    # Ink
                (255, 255, 0),  # Jig
                (255, 0, 255),  # Machining
                (0, 255, 255),  # Overcut
                (128, 128, 0),  # Pocket
                (128, 0, 128)   # Scratches
            ]
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    def preprocess_hrnet_image(self,image_path, img_size=512, device='cpu'):

        original_image = cv2.imread(image_path)
        if original_image is None:
            raise FileNotFoundError(f"Image not found at {image_path}")

        resized_image = cv2.resize(original_image, (img_size, img_size))

        rgb_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)

        normalized_image = rgb_image.astype(np.float32) / 255.0

        image_tensor = torch.tensor(normalized_image).permute(2, 0, 1).unsqueeze(0).to(device)

        return image_tensor, original_image #it will return the original image for visualization purposes and normalized image tensor


    def predict_hrnet(self,image_path, model, device, img_size=512, threshold=0.5):
        #Returns (original_image_bgr, pred_masks_binary, pred_masks_probs): original BGR image, binary masks (C, H, W), and probability maps (C, H, W) prob map is used to check ofr thres bianry mask is 0/1
        model.eval()

        # Preprocess the image
        input_tensor, original_image_bgr = self.preprocess_hrnet_image(image_path, img_size=img_size, device=device)

        with torch.no_grad():
            output = model(input_tensor)

        # Apply sigmoid and threshold for binary masks
        pred_probs = torch.sigmoid(output).squeeze(0).cpu().numpy()  # (C, H, W)
        pred_masks_binary = (pred_probs > threshold).astype(np.uint8)

        return original_image_bgr, pred_masks_binary, pred_probs

    def visualize_hrnet_prediction(#this is gpt i was bored doing this :) so if any error i dont know where it is :D
        self,
        original_image_bgr,
        pred_masks_binary,
        pred_masks_probs,
        class_names,
        colors,
        threshold=0.3
    ):

        # Convert to RGB
        original_image_rgb = cv2.cvtColor(original_image_bgr, cv2.COLOR_BGR2RGB)
        vis_img = original_image_rgb.copy()

        h, w = vis_img.shape[:2]

        for c_idx in range(pred_masks_probs.shape[0]):

            # 🔹 Use probability mask
            mask = (pred_masks_probs[c_idx] > threshold).astype(np.uint8)

            # Resize if needed
            if mask.shape != (h, w):
                mask = cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST)

            # Skip empty masks
            if np.sum(mask) == 0:
                continue

            # 🔹 Clean mask (helps tiny defects)
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

            # 🔹 Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            color = tuple(int(c) for c in colors[c_idx])

            for cnt in contours:

                area = cv2.contourArea(cnt)

                # Keep small defects but remove noise
                if area < 3:
                    continue

                # 🔹 Draw contour
                cv2.drawContours(vis_img, [cnt], -1, color, 2)

                # 🔹 Bounding box
                x, y, w_box, h_box = cv2.boundingRect(cnt)
                cv2.rectangle(vis_img, (x, y), (x + w_box, y + h_box), color, 2)

                # 🔹 ===== BIG LABEL PART =====

                label = class_names[c_idx]

                # Adaptive font size (key fix)
                font_scale = max(0.7, min(h, w) / 600)
                thickness = int(max(2, font_scale * 2))

                # Get text size
                (text_w, text_h), _ = cv2.getTextSize(
                    label,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale,
                    thickness
                )

                # Decide label position (avoid going outside)
                if y < 40:
                    y_text = y + text_h + 10
                else:
                    y_text = y

                # Draw label background box
                cv2.rectangle(
                    vis_img,
                    (x, y_text - text_h - 10),
                    (x + text_w + 10, y_text),
                    color,
                    -1
                )

                # Put label text
                cv2.putText(
                    vis_img,
                    label,
                    (x + 5, y_text - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale,
                    (255, 255, 255),
                    thickness,
                    cv2.LINE_AA
                )

        # 🔹 Plot
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        axes[0].imshow(original_image_rgb)
        axes[0].set_title("Original")
        axes[0].axis("off")

        axes[1].imshow(vis_img)
        axes[1].set_title(f"Boxes + Contours + Labels (thr={threshold})")
        axes[1].axis("off")

        plt.tight_layout()
        cv2.imwrite("output.png", cv2.cvtColor(vis_img, cv2.COLOR_RGB2BGR))
        plt.show()
        return vis_img
    
#testing
if __name__ == "__main__":
    #call class
    inference = hr_net_inference()

    if 'model' not in globals():
        model = smp.FPN(#architecture must match training
            encoder_name="timm-regnety_032",
            encoder_weights="imagenet",
            in_channels=3,
            classes=inference.NUM_CLASSES,
            )
        model.load_state_dict(torch.load("hr_net.pth", map_location=torch.device("cpu")))#load weights ill send u 
        model.to(inference.device)

        inference_threshold = 0.8 # i tried this for 0.8 model is highly confident if u think any thing is getting missed use 0.5

        image_path = r"C:\Users\HP\Downloads\3803fc1e-12b0-4786-a822-3a0d0ef1f3a4.jpg"#replace with your image path
        # Run prediction
        original_img, predicted_masks, predicted_probs = inference.predict_hrnet(
            image_path,#call this dynamically u will get original image and predicted masks and probs from predict func
            model,
            inference.device,
            img_size=512, # Ensure this matches training img_size
            threshold=inference_threshold
        )

        # Visualize the results
    image_pred = inference.visualize_hrnet_prediction(#it will return the original image with boxes and labels
            original_img,
            predicted_masks,
            predicted_probs,
            inference.CLASS_NAMES,
            inference.COLORS,
            threshold=inference_threshold
        )
    cv2.imwrite("final_output.png", cv2.cvtColor(image_pred, cv2.COLOR_RGB2BGR))#saving u can show it in frontend but i saved for reference