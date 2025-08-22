import React, { useState } from 'react';
import { Box, Button, Typography } from '@mui/material';

const steps = [
  {
    title: 'Welcome to Jarvis!',
    content: 'This tutorial will walk you through the basics of using Jarvis.',
  },
  {
    title: 'The Chat Interface',
    content: 'This is the main interface for interacting with Jarvis. You can type your commands in the text box at the bottom of the screen.',
  },
  {
    title: 'The Supreme Dashboard',
    content: 'The supreme dashboard provides a high-level overview of Jarvis\'s capabilities. You can access it by clicking the floating action button in the bottom-right corner of the screen.',
  },
  {
    title: 'The Voice Interface',
    content: 'You can also interact with Jarvis by voice. To activate the voice interface, click the microphone icon next to the text input field.',
  },
];

const Tutorial: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  return (
    <Box>
      <Typography variant="h4">{steps[activeStep].title}</Typography>
      <Typography variant="body1">{steps[activeStep].content}</Typography>
      <Box>
        <Button disabled={activeStep === 0} onClick={handleBack}>
          Back
        </Button>
        <Button variant="contained" color="primary" onClick={handleNext}>
          {activeStep === steps.length - 1 ? 'Finish' : 'Next'}
        </Button>
      </Box>
    </Box>
  );
};

export default Tutorial;
