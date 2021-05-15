import React from 'react';
import ReactDOM from 'react-dom';
import { Router, Switch, Route } from 'react-router-dom';
import './index.css';
import App from './components/App';
import Blockchain from './components/Blockchain';
import ConductTransaction from './components/ConductTransaction';
import TransactionPool from './components/TransactionPool';
import history from './history';


ReactDOM.render(
  <Router history={history}>
    <Switch>
      <Route component={App} path='/' exact />
      <Route component={Blockchain} path='/blockchain' />
      <Route component={ConductTransaction} path='/conduct-transaction' />
      <Route component={TransactionPool} path='/transaction-pool' />
    </Switch>
  </Router>,
  document.getElementById('root')
);
