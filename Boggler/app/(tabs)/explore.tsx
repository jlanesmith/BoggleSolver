import React, { useState, useEffect, useRef } from 'react';
import { Button, View, StyleSheet, TouchableOpacity, Text, Image } from 'react-native';
import { CameraView, CameraType, useCameraPermissions } from 'expo-camera';
import { useRouter } from 'expo-router';
import { useWords } from '../words_context'; // Import the provider

const CameraScreen = () => {
  const router = useRouter();
  const cameraRef = useRef(null);
  const { setWords } = useWords(); // Get setWords from context

  const [photoUri, setPhotoUri] = useState(null);

  const [facing, setFacing] = useState<CameraType>('back');
  const [permission, requestPermission] = useCameraPermissions();

  if (!permission) {
    // Camera permissions are still loading.
    return <View />;
  }

  if (!permission.granted) {
    // Camera permissions are not granted yet.
    return (
      <View style={styles.container}>
        <Text style={styles.message}>We need your permission to show the camera</Text>
        <Button onPress={requestPermission} title="grant permission" />
      </View>
    );
  }

  function toggleCameraFacing() {
    setFacing(current => (current === 'back' ? 'front' : 'back'));
  }

  const takePicture = async () => {
    if (cameraRef.current) {
      try {
        const options = { quality: 1, base64: false };
        const data = await cameraRef.current.takePictureAsync(options);
        setPhotoUri(data.uri)
        console.log('Picture taken:', data.uri);
  
        // Prepare the image data for the API call
        const formData = new FormData();
        formData.append('image', {
          uri: data.uri,
          type: 'image/jpg', // or 'image/png' based on your output
          name: 'photo.jpg',
        });
  
        // Make the API call
        const response = await fetch('http://10.0.0.108:5001/process-image', {
          method: 'POST',
          // headers: {
          //   'Content-Type': 'multipart/form-data',
          // },
          body: formData,
        });
  
        if (response.ok) {
          const responseData = await response.json();
          console.log('API response:', responseData);
          let words = responseData.words;
          console.log(words);
          setWords(words);
          router.push('/results');
          // Handle the response data
        } else {
          console.error('API call failed with status:', response.status);
        }
      } catch (error) {
        console.error('Error taking picture or making API call:', error);
      }
    } else {
      console.warn('Camera reference is not set.');
    }
  };
  

  return (
    <View style={styles.container}>
      <CameraView style={styles.camera} facing={facing} ref={cameraRef}>
        <View style={styles.buttonContainer}>
          <TouchableOpacity style={styles.button} onPress={toggleCameraFacing}>
            <Button title="Go to Results" onPress={takePicture} />
            <Text style={styles.text}>Flip Camera</Text>
          </TouchableOpacity>
        </View>
      </CameraView>
    </View>
  );  
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
  },
  message: {
    textAlign: 'center',
    paddingBottom: 10,
  },
  camera: {
    flex: 1,
  },
  buttonContainer: {
    flex: 1,
    flexDirection: 'row',
    backgroundColor: 'transparent',
    margin: 164,
  },
  button: {
    flex: 1,
    alignSelf: 'flex-end',
    alignItems: 'center',
  },
  text: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
  },
  imagePreview: {
    flex: 1,
    resizeMode: 'cover',
  },
});

export default CameraScreen;
