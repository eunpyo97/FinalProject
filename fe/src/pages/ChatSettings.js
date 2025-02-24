import React, { useState } from "react";
import styled from "styled-components";

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
`;

const SettingsForm = styled.form`
  width: 80%;
  max-width: 500px;
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

const Label = styled.label`
  font-weight: bold;
`;

const Checkbox = styled.input`
  margin-right: 10px;
`;

const Button = styled.button`
  padding: 10px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  &:hover {
    background-color: #0056b3;
  }
`;

const ChatSettings = ({ onSaveSettings }) => {
  const [settings, setSettings] = useState({
    webcamEnabled: false,
  });

  const handleChange = (e) => {
    const { name, checked } = e.target;
    setSettings({ ...settings, [name]: checked });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSaveSettings(settings);
    alert("설정이 저장되었습니다!");
  };

  return (
    <Container>
      <h1>챗봇 설정</h1>
      <SettingsForm onSubmit={handleSubmit}>
        <Label>
          <Checkbox
            type="checkbox"
            name="webcamEnabled"
            checked={settings.webcamEnabled}
            onChange={handleChange}
          />
          웹캠 자동 활성화
        </Label>
        <Button type="submit">저장</Button>
      </SettingsForm>
    </Container>
  );
};

export default ChatSettings;