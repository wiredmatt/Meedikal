import React from "react";
import { Landing as MeedikalLanding } from "./landing";
import { App as MeedikalApp } from "./app";
import { Route, Switch, BrowserRouter } from "react-router-dom";
import { NotFound } from "./components/notFound";

interface IProps {}

const App: React.FC<IProps> = () => {
  return (
    <BrowserRouter>
      <Switch>
        <Route path="/app">
          <MeedikalApp />
        </Route>
        <Route exact path="/">
          <MeedikalLanding />
        </Route>
        <Route component={NotFound}/>
      </Switch>
    </BrowserRouter>
  );
};

export default App;
