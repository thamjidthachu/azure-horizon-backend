# User Profile and Avatar Update API Documentation

This document describes the APIs for updating user profile information and managing user avatars.

## Table of Contents
- [Authentication](#authentication)
- [Profile Update API](#profile-update-api)
- [Avatar Update API](#avatar-update-api)
- [Error Handling](#error-handling)
- [Examples](#examples)

---

## Authentication

All endpoints require JWT authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

---

## Profile Update API

### Endpoint
```
PUT/PATCH /api/auth/profile/update/
```

### Description
Update user profile information including username, full name, email, phone, and gender.

### HTTP Methods
- **PUT**: Full update (all fields should be provided)
- **PATCH**: Partial update (only provide fields you want to update)

### Request Headers
```
Content-Type: application/json
Authorization: Bearer <access_token>
```

### Request Body Parameters

| Field      | Type   | Required | Description                           |
|------------|--------|----------|---------------------------------------|
| username   | string | No       | Unique username                       |
| full_name  | string | No       | User's full name                      |
| email      | string | No       | Unique email address                  |
| phone      | string | No       | Phone number                          |
| gender     | string | No       | Gender ('M', 'F', or other options)   |

### Response

#### Success Response (200 OK)
```json
{
  "user": {
    "id": 1,
    "avatar": "http://example.com/media/avatars/user_avatar.jpg",
    "username": "johndoe",
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "gender": "M",
    "is_active": true
  },
  "message": "Profile updated successfully."
}
```

#### Error Response (400 Bad Request)
```json
{
  "username": ["This username is already in use."],
  "email": ["This email is already in use."]
}
```

### Validation Rules
- **Username**: Must be unique across all users (excluding current user)
- **Email**: Must be unique across all users (excluding current user)
- **All fields**: Optional for PATCH requests

---

## Avatar Update API

### Endpoint
```
PUT/PATCH/DELETE /api/auth/profile/avatar/
```

### Description
Upload, update, or delete user profile avatar image.

### HTTP Methods
- **PUT**: Upload/update avatar
- **PATCH**: Upload/update avatar (same as PUT)
- **DELETE**: Remove current avatar

### Upload/Update Avatar

#### Request Headers
```
Content-Type: multipart/form-data
Authorization: Bearer <access_token>
```

#### Request Body Parameters

| Field  | Type | Required | Description                    |
|--------|------|----------|--------------------------------|
| avatar | file | Yes      | Image file (JPEG, PNG, GIF, WebP) |

#### File Validation
- **Maximum file size**: 5MB
- **Allowed formats**: JPEG, JPG, PNG, GIF, WebP
- **Old avatar**: Automatically deleted when uploading new one

#### Success Response (200 OK)
```json
{
  "user": {
    "id": 1,
    "avatar": "http://example.com/media/avatars/new_avatar.jpg",
    "username": "johndoe",
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "gender": "M",
    "is_active": true
  },
  "message": "Avatar updated successfully."
}
```

#### Error Response (400 Bad Request)
```json
{
  "avatar": ["Avatar file size should not exceed 5MB."]
}
```

OR

```json
{
  "avatar": ["Invalid file type. Only JPEG, PNG, GIF, and WebP images are allowed."]
}
```

### Delete Avatar

#### Request Headers
```
Authorization: Bearer <access_token>
```

#### Success Response (200 OK)
```json
{
  "user": {
    "id": 1,
    "avatar": null,
    "username": "johndoe",
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "gender": "M",
    "is_active": true
  },
  "message": "Avatar deleted successfully."
}
```

#### Error Response (404 Not Found)
```json
{
  "message": "No avatar to delete."
}
```

---

## Error Handling

### Common Error Responses

#### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

OR

```json
{
  "detail": "Given token not valid for any token type"
}
```

#### 400 Bad Request
```json
{
  "field_name": ["Error message describing the validation issue."]
}
```

#### 500 Internal Server Error
```json
{
  "error": "Failed to delete avatar."
}
```

---

## Examples

### Example 1: Update Full Name and Phone (PATCH)

**Request:**
```bash
curl -X PATCH http://localhost:8000/api/auth/profile/update/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Michael Doe",
    "phone": "+1987654321"
  }'
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "avatar": "http://example.com/media/avatars/user_avatar.jpg",
    "username": "johndoe",
    "full_name": "John Michael Doe",
    "email": "john.doe@example.com",
    "phone": "+1987654321",
    "gender": "M",
    "is_active": true
  },
  "message": "Profile updated successfully."
}
```

### Example 2: Update Email (PATCH)

**Request:**
```bash
curl -X PATCH http://localhost:8000/api/auth/profile/update/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.new@example.com"
  }'
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "avatar": "http://example.com/media/avatars/user_avatar.jpg",
    "username": "johndoe",
    "full_name": "John Michael Doe",
    "email": "john.new@example.com",
    "phone": "+1987654321",
    "gender": "M",
    "is_active": true
  },
  "message": "Profile updated successfully."
}
```

### Example 3: Upload Avatar

**Request:**
```bash
curl -X PUT http://localhost:8000/api/auth/profile/avatar/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -F "avatar=@/path/to/image.jpg"
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "avatar": "http://example.com/media/avatars/image_abc123.jpg",
    "username": "johndoe",
    "full_name": "John Michael Doe",
    "email": "john.new@example.com",
    "phone": "+1987654321",
    "gender": "M",
    "is_active": true
  },
  "message": "Avatar updated successfully."
}
```

### Example 4: Delete Avatar

**Request:**
```bash
curl -X DELETE http://localhost:8000/api/auth/profile/avatar/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "avatar": null,
    "username": "johndoe",
    "full_name": "John Michael Doe",
    "email": "john.new@example.com",
    "phone": "+1987654321",
    "gender": "M",
    "is_active": true
  },
  "message": "Avatar deleted successfully."
}
```

### Example 5: Full Profile Update (PUT)

**Request:**
```bash
curl -X PUT http://localhost:8000/api/auth/profile/update/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe_updated",
    "full_name": "John Michael Doe Jr.",
    "email": "john.jr@example.com",
    "phone": "+1122334455",
    "gender": "M"
  }'
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "avatar": "http://example.com/media/avatars/image_abc123.jpg",
    "username": "johndoe_updated",
    "full_name": "John Michael Doe Jr.",
    "email": "john.jr@example.com",
    "phone": "+1122334455",
    "gender": "M",
    "is_active": true
  },
  "message": "Profile updated successfully."
}
```

---

## Frontend Integration Examples

### JavaScript/Fetch Example - Update Profile

```javascript
async function updateProfile(profileData, accessToken) {
  try {
    const response = await fetch('http://localhost:8000/api/auth/profile/update/', {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify(profileData)
    });

    const data = await response.json();
    
    if (response.ok) {
      console.log('Profile updated:', data.user);
      return data;
    } else {
      console.error('Update failed:', data);
      throw new Error(data);
    }
  } catch (error) {
    console.error('Error updating profile:', error);
    throw error;
  }
}

// Usage
const profileData = {
  full_name: "John Doe",
  phone: "+1234567890"
};

updateProfile(profileData, 'your_access_token_here');
```

### JavaScript/Fetch Example - Upload Avatar

```javascript
async function uploadAvatar(file, accessToken) {
  try {
    const formData = new FormData();
    formData.append('avatar', file);

    const response = await fetch('http://localhost:8000/api/auth/profile/avatar/', {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      },
      body: formData
    });

    const data = await response.json();
    
    if (response.ok) {
      console.log('Avatar updated:', data.user.avatar);
      return data;
    } else {
      console.error('Upload failed:', data);
      throw new Error(data);
    }
  } catch (error) {
    console.error('Error uploading avatar:', error);
    throw error;
  }
}

// Usage with file input
const fileInput = document.getElementById('avatar-input');
fileInput.addEventListener('change', (event) => {
  const file = event.target.files[0];
  if (file) {
    uploadAvatar(file, 'your_access_token_here');
  }
});
```

### React Example - Profile Update Form

```jsx
import React, { useState } from 'react';

function ProfileUpdateForm({ accessToken, currentUser }) {
  const [formData, setFormData] = useState({
    username: currentUser.username,
    full_name: currentUser.full_name,
    email: currentUser.email,
    phone: currentUser.phone,
    gender: currentUser.gender
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/auth/profile/update/', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (response.ok) {
        alert('Profile updated successfully!');
        // Update user state in your app
      } else {
        setError(data);
      }
    } catch (err) {
      setError({ message: 'Network error occurred' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        name="username"
        value={formData.username}
        onChange={handleChange}
        placeholder="Username"
      />
      <input
        type="text"
        name="full_name"
        value={formData.full_name}
        onChange={handleChange}
        placeholder="Full Name"
      />
      <input
        type="email"
        name="email"
        value={formData.email}
        onChange={handleChange}
        placeholder="Email"
      />
      <input
        type="tel"
        name="phone"
        value={formData.phone}
        onChange={handleChange}
        placeholder="Phone"
      />
      <select name="gender" value={formData.gender} onChange={handleChange}>
        <option value="M">Male</option>
        <option value="F">Female</option>
      </select>
      
      {error && <div className="error">{JSON.stringify(error)}</div>}
      
      <button type="submit" disabled={loading}>
        {loading ? 'Updating...' : 'Update Profile'}
      </button>
    </form>
  );
}
```

---

## Notes

1. **Authentication Required**: All endpoints require a valid JWT access token
2. **File Upload**: Use `multipart/form-data` for avatar uploads
3. **Old Avatar Cleanup**: When uploading a new avatar, the old one is automatically deleted
4. **Validation**: Username and email must be unique across the system
5. **Partial Updates**: Use PATCH to update only specific fields
6. **Full Updates**: Use PUT to update all fields at once
7. **Logging**: All profile and avatar updates are logged for audit purposes

---

## API Endpoints Summary

| Endpoint                      | Method | Description                    | Auth Required |
|-------------------------------|--------|--------------------------------|---------------|
| `/api/auth/profile/update/`   | PUT    | Full profile update            | Yes           |
| `/api/auth/profile/update/`   | PATCH  | Partial profile update         | Yes           |
| `/api/auth/profile/avatar/`   | PUT    | Upload/update avatar           | Yes           |
| `/api/auth/profile/avatar/`   | PATCH  | Upload/update avatar           | Yes           |
| `/api/auth/profile/avatar/`   | DELETE | Delete avatar                  | Yes           |
