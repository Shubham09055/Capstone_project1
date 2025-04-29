import React, {useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { TextField, Button, Typography, Paper } from '@mui/material';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import AuthContext from '../../context/auth';

const Register = () => {
  const { register, error } = useContext(AuthContext);
  const navigate = useNavigate();

  const initialValues = {
    name: '',
    email: '',
    password: '',
  };

  const validationSchema = Yup.object().shape({
    name: Yup.string().required('Required'),
    email: Yup.string().email('Invalid email').required('Required'),
    password: Yup.string().min(6, 'Password must be at least 6 characters').required('Required'),
  });

  const onSubmit = async (values, { setSubmitting }) => {
    await register(values);
    setSubmitting(false);
  };

  return (
    <Paper style={{ padding: '2rem', maxWidth: '400px', margin: '2rem auto' }}>
      <Typography variant="h4" align="center" gutterBottom>
        Register
      </Typography>
      {error && (
        <Typography color="error" align="center" gutterBottom>
          {error}
        </Typography>
      )}
      <Formik
        initialValues={initialValues}
        validationSchema={validationSchema}
        onSubmit={onSubmit}
      >
        {({ isSubmitting }) => (
          <Form>
            <Field
              as={TextField}
              name="name"
              label="Name"
              fullWidth
              margin="normal"
              variant="outlined"
            />
            <ErrorMessage name="name" component="div" />
            
            <Field
              as={TextField}
              name="email"
              label="Email"
              fullWidth
              margin="normal"
              variant="outlined"
            />
            <ErrorMessage name="email" component="div" />
            
            <Field
              as={TextField}
              name="password"
              label="Password"
              type="password"
              fullWidth
              margin="normal"
              variant="outlined"
            />
            <ErrorMessage name="password" component="div" />
            
            <Button
              type="submit"
              variant="contained"
              color="primary"
              fullWidth
              disabled={isSubmitting}
              style={{ marginTop: '1rem' }}
            >
              Register
            </Button>
          </Form>
        )}
      </Formik>
      <Typography style={{ marginTop: '1rem' }}>
        Already have an account?{' '}
        <Button color="primary" onClick={() =>  navigate('/login')}>
          Login
        </Button>
      </Typography>
    </Paper>
  );
};

export default Register;