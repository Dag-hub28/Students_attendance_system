# How to Test the Attendance System

## Quick Test (5 minutes)

1. **Run the app:**
   ```bash
   .venv\Scripts\python.exe app.py
   ```

2. **Open browser:** Go to `http://localhost:5000`

3. **Register:** Click "Register" and create a student account

4. **Enroll your face:**
   - Login with your new account
   - Click "👤 Register Face" 
   - Allow camera access
   - Take a clear photo of your face
   - Click "I Consent" when prompted

5. **Test recognition:**
   - Go to Dashboard → "📸 Test Face Recognition" 
   - Click "📷 Capture & Test Recognition"
   - Check if your name appears in the result

## What to Expect
- Response time: <10ms (very fast)
- Detection depends on face quality and lighting

## For 90% Accuracy Target
- Need 30+ volunteers to enroll faces
- Each person should enroll 2-3 samples (different lighting)
- Test with varied conditions: bright, dim, backlight