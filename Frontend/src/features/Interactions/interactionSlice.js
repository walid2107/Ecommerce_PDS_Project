import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { toast } from "react-toastify";
import {interactionSevice} from "./interactionService"

export const addInteraction = createAsyncThunk(
    "interaction",
    async (data, thunkAPI) => {
      try {
        return await interactionSevice.createInteraction(data);
      } catch (error) {
        return thunkAPI.rejectWithValue(error);
      }
    }
  );