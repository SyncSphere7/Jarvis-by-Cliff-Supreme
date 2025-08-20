import React from 'react'
import {
  Box,
  Paper,
  Typography,
  Button,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material'
import {
  Code,
  Analytics,
  Security,
  Build,
  Psychology,
  Speed,
  ExpandMore,
  Rocket,
  AutoAwesome,
  DataObject,
} from '@mui/icons-material'
import { useDispatch, useSelector } from 'react-redux'
import { RootState } from '../store/store'
import { setCurrentInput } from '../store/chatSlice'

const quickActions = [
  {
    category: 'Development',
    icon: <Code />,
    actions: [
      {
        title: 'Code Review',
        description: 'Analyze and improve code quality',
        template: 'Please review this code and suggest improvements for better performance, security, and maintainability.',
      },
      {
        title: 'Debug Assistant',
        description: 'Help debug and fix issues',
        template: 'I\'m having an issue with my code. Can you help me debug and find the problem?',
      },
      {
        title: 'Architecture Design',
        description: 'Design system architecture',
        template: 'Help me design a scalable architecture for a web application with microservices.',
      },
    ],
  },
  {
    category: 'Analysis',
    icon: <Analytics />,
    actions: [
      {
        title: 'Performance Analysis',
        description: 'Analyze system performance',
        template: 'Analyze the performance bottlenecks in my application and suggest optimizations.',
      },
      {
        title: 'Data Analysis',
        description: 'Analyze data patterns',
        template: 'Help me analyze this dataset and identify key patterns and insights.',
      },
      {
        title: 'Market Research',
        description: 'Research market trends',
        template: 'Provide a comprehensive analysis of current market trends in the tech industry.',
      },
    ],
  },
  {
    category: 'Security',
    icon: <Security />,
    actions: [
      {
        title: 'Security Audit',
        description: 'Audit security vulnerabilities',
        template: 'Perform a security audit of my application and identify potential vulnerabilities.',
      },
      {
        title: 'Quantum Encryption',
        description: 'Implement quantum-resistant security',
        template: 'Help me implement quantum-resistant encryption for my API endpoints.',
      },
      {
        title: 'Threat Assessment',
        description: 'Assess security threats',
        template: 'Analyze potential security threats for my system and recommend countermeasures.',
      },
    ],
  },
]

const Sidebar: React.FC = () => {
  const dispatch = useDispatch()
  const { godlikeMode } = useSelector((state: RootState) => state.system)

  const handleQuickAction = (template: string) => {
    dispatch(setCurrentInput(template))
  }

  return (
    <Paper
      sx={{
        height: '100%',
        borderRadius: 0,
        borderRight: 1,
        borderColor: 'divider',
        overflow: 'auto',
      }}
    >
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        
        {godlikeMode && (
          <Chip
            icon={<AutoAwesome />}
            label="Godlike Powers Active"
            color="warning"
            variant="filled"
            sx={{ mb: 2, fontWeight: 'bold' }}
          />
        )}
      </Box>

      <Divider />

      {/* Quick Action Categories */}
      {quickActions.map((category) => (
        <Accordion key={category.category} defaultExpanded>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {category.icon}
              <Typography variant="subtitle1" fontWeight="medium">
                {category.category}
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails sx={{ pt: 0 }}>
            <List dense>
              {category.actions.map((action) => (
                <ListItem
                  key={action.title}
                  button
                  onClick={() => handleQuickAction(action.template)}
                  sx={{
                    borderRadius: 1,
                    mb: 0.5,
                    '&:hover': {
                      backgroundColor: 'action.hover',
                    },
                  }}
                >
                  <ListItemText
                    primary={action.title}
                    secondary={action.description}
                    primaryTypographyProps={{ variant: 'body2', fontWeight: 'medium' }}
                    secondaryTypographyProps={{ variant: 'caption' }}
                  />
                </ListItem>
              ))}
            </List>
          </AccordionDetails>
        </Accordion>
      ))}

      <Divider sx={{ my: 2 }} />

      {/* Supreme Templates */}
      <Box sx={{ p: 2 }}>
        <Typography variant="subtitle1" gutterBottom fontWeight="medium">
          Supreme Templates
        </Typography>
        
        <List dense>
          <ListItem
            button
            onClick={() => handleQuickAction('Create a full-stack application with React, Node.js, and PostgreSQL with quantum-secure authentication.')}
            sx={{ borderRadius: 1, mb: 0.5 }}
          >
            <ListItemIcon>
              <Rocket />
            </ListItemIcon>
            <ListItemText
              primary="Full-Stack App"
              secondary="Complete application setup"
              primaryTypographyProps={{ variant: 'body2' }}
              secondaryTypographyProps={{ variant: 'caption' }}
            />
          </ListItem>
          
          <ListItem
            button
            onClick={() => handleQuickAction('Design a microservices architecture that can scale to handle 1 million concurrent users.')}
            sx={{ borderRadius: 1, mb: 0.5 }}
          >
            <ListItemIcon>
              <Speed />
            </ListItemIcon>
            <ListItemText
              primary="Scalable Architecture"
              secondary="Million-user capacity"
              primaryTypographyProps={{ variant: 'body2' }}
              secondaryTypographyProps={{ variant: 'caption' }}
            />
          </ListItem>
          
          <ListItem
            button
            onClick={() => handleQuickAction('Implement AI-powered analytics dashboard with real-time data processing and machine learning predictions.')}
            sx={{ borderRadius: 1, mb: 0.5 }}
          >
            <ListItemIcon>
              <Psychology />
            </ListItemIcon>
            <ListItemText
              primary="AI Analytics"
              secondary="ML-powered insights"
              primaryTypographyProps={{ variant: 'body2' }}
              secondaryTypographyProps={{ variant: 'caption' }}
            />
          </ListItem>
          
          <ListItem
            button
            onClick={() => handleQuickAction('Create a comprehensive API with GraphQL, REST endpoints, real-time subscriptions, and automatic documentation.')}
            sx={{ borderRadius: 1 }}
          >
            <ListItemIcon>
              <DataObject />
            </ListItemIcon>
            <ListItemText
              primary="Supreme API"
              secondary="GraphQL + REST + Docs"
              primaryTypographyProps={{ variant: 'body2' }}
              secondaryTypographyProps={{ variant: 'caption' }}
            />
          </ListItem>
        </List>
      </Box>
    </Paper>
  )
}

export default Sidebar