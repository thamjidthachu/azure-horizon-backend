# User Profile and Avatar Update API - Quick Start Guide

## 🎉 What's New

Two new API endpoints have been added to manage user profiles and avatars:

1. **Profile Update API** - `/api/auth/profile/update/`
2. **Avatar Management API** - `/api/auth/profile/avatar/`

---

## 📋 Quick Reference

### Endpoints Summary

| Endpoint | Method | Purpose | Auth Required |
|----------|--------|---------|---------------|
| `/api/auth/profile/update/` | PUT | Full profile update | ✅ Yes |
| `/api/auth/profile/update/` | PATCH | Partial profile update | ✅ Yes |
| `/api/auth/profile/avatar/` | PUT/PATCH | Upload/update avatar | ✅ Yes |
| `/api/auth/profile/avatar/` | DELETE | Delete avatar | ✅ Yes |

---

## 🚀 Quick Start

### 1. Update User Profile

**Partial Update (PATCH) - Recommended**
```bash
curl -X PATCH http://localhost:8000/api/auth/profile/update/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "phone": "+1234567890"
  }'
```

**Full Update (PUT)**
```bash
curl -X PUT http://localhost:8000/api/auth/profile/update/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "gender": "M"
  }'
```

### 2. Upload Avatar

```bash
curl -X PUT http://localhost:8000/api/auth/profile/avatar/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "avatar=@/path/to/image.jpg"
```

### 3. Delete Avatar

```bash
curl -X DELETE http://localhost:8000/api/auth/profile/avatar/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📝 Editable Fields

### Profile Update
- `username` - Unique username
- `full_name` - User's full name
- `email` - Unique email address
- `phone` - Phone number
- `gender` - Gender (M/F/etc.)

### Avatar Upload
- `avatar` - Image file (JPEG, PNG, GIF, WebP)
- Maximum size: 5MB
- Old avatar automatically deleted on new upload

---

## ✅ Validation Rules

### Username & Email
- Must be unique across all users
- Current user excluded from uniqueness check

### Avatar
- **Allowed formats**: JPEG, JPG, PNG, GIF, WebP
- **Maximum size**: 5MB
- **Auto-cleanup**: Old avatar deleted when uploading new one

---

## 📦 Files Added/Modified

### New Files
1. `docs/API_USER_PROFILE_UPDATE.md` - Complete API documentation
2. `docs/Postman_Profile_Avatar_API.json` - Postman collection
3. `apps/authentication/tests.py` - Comprehensive test suite

### Modified Files
1. `apps/authentication/serializers.py` - Added ProfileUpdateSerializer & AvatarUpdateSerializer
2. `apps/authentication/views.py` - Added ProfileUpdateView & AvatarUpdateView
3. `apps/authentication/urls.py` - Added new URL patterns

---

## 🧪 Testing

### Run Unit Tests
```bash
python manage.py test apps.authentication.tests
```

### Test Specific Cases
```bash
# Test profile update
python manage.py test apps.authentication.tests.ProfileUpdateAPITestCase

# Test avatar upload
python manage.py test apps.authentication.tests.AvatarUpdateAPITestCase
```

### Import Postman Collection
1. Open Postman
2. Import `docs/Postman_Profile_Avatar_API.json`
3. Set `base_url` variable to your server URL
4. Login to get access token (auto-saved to collection variable)
5. Test all endpoints

---

## 🔒 Authentication

All endpoints require JWT authentication:

```
Authorization: Bearer <your_access_token>
```

Get your access token by logging in:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

---

## 📖 Full Documentation

For complete API documentation with all examples, see:
- `docs/API_USER_PROFILE_UPDATE.md`

---

## 💡 Usage Examples

### Example 1: Update only email
```json
PATCH /api/auth/profile/update/
{
  "email": "newemail@example.com"
}
```

### Example 2: Update name and phone
```json
PATCH /api/auth/profile/update/
{
  "full_name": "Jane Smith",
  "phone": "+9876543210"
}
```

### Example 3: Change username
```json
PATCH /api/auth/profile/update/
{
  "username": "janesmith"
}
```

---

## ⚠️ Common Errors

### 400 Bad Request
- Duplicate username or email
- Invalid file type for avatar
- File size exceeds 5MB

### 401 Unauthorized
- Missing or invalid access token
- Token expired (use refresh token)

### 404 Not Found
- Trying to delete avatar when none exists

---

## 🎯 Response Format

All successful requests return:
```json
{
  "user": {
    "id": 1,
    "avatar": "http://example.com/media/avatars/avatar.jpg",
    "username": "johndoe",
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "gender": "M",
    "is_active": true
  },
  "message": "Profile updated successfully."
}
```

---

## 🔧 Implementation Details

### Serializers
- `ProfileUpdateSerializer` - Handles profile field updates with validation
- `AvatarUpdateSerializer` - Handles avatar file uploads with validation

### Views
- `ProfileUpdateView` - Supports PUT (full) and PATCH (partial) updates
- `AvatarUpdateView` - Supports PUT/PATCH (upload) and DELETE operations

### Features
- ✅ Automatic old avatar cleanup
- ✅ File type and size validation
- ✅ Unique username/email validation
- ✅ Comprehensive logging
- ✅ Full test coverage
- ✅ JWT authentication

---

## 📞 Support

For issues or questions, refer to the full documentation in `docs/API_USER_PROFILE_UPDATE.md`
