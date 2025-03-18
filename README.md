# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react/README.md) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript and enable type-aware lint rules. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.



# 📸 Smart Recipe Generator with AI & YOLOv8

This project uses a pre-trained AI model and YOLOv8 object detection to generate recipes from detected ingredients via image or text input.

## 🚀 Project Structure

```
.
├── backend/
│   ├── main.py
│   ├── imagerecognition.py
│   ├── recipegenerator.py
│   ├── yolov8s.pt   <-- Large model file (stored with Git LFS)
│   ├── static/
│   └── requirements.txt
└── frontend/
    ├── src/
    ├── package.json
    └── vite.config.js
```

---

## 📂 YOLOv8 Model File with Git LFS

This project uses a large YOLOv8 model file (`yolov8s.pt`) stored with **Git Large File Storage (LFS)**.

### ✅ Setup Instructions for Team Members:

1. **Install Git LFS (only once per machine):**
   - Download from [git-lfs.com](https://git-lfs.com)
   - Or use terminal:
   ```bash
   git lfs install
   ```

2. **Clone the repository as usual:**
   ```bash
   git clone https://github.com/your-org/your-repo-name.git
   cd your-repo-name
   ```

3. **Fetch large files managed by LFS:**
   ```bash
   git lfs pull
   ```

4. ✅ You should now have `backend/yolov8s.pt` downloaded automatically.

---

### ✅ For contributors adding new large files:
- Track large files:
   ```bash
   git lfs track "*.pt"
   ```
- Then add and push as usual:
   ```bash
   git add backend/yolov8s.pt
   git commit -m "Add YOLOv8 model via Git LFS"
   git push
   ```

---

## 🛠 Deployment Notes
- The backend can be deployed on **Render.com** or **Railway** (consider memory limits for YOLO & Transformers).
- The frontend can be deployed on **Vercel** or **Netlify**.

---

## 📚 Helpful Links:
- [Git LFS Documentation](https://git-lfs.github.com)
- [Render Deployment Docs](https://render.com/docs/deploy-fastapi)
- [YOLOv8 Official](https://docs.ultralytics.com/)
- [Hugging Face Recipe Generator Model](https://huggingface.co/flax-community/t5-recipe-generation)

---