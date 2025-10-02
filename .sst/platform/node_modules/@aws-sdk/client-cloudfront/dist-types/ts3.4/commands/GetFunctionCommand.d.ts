import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import { Uint8ArrayBlobAdapter } from "@smithy/util-stream";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import { GetFunctionRequest, GetFunctionResult } from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetFunctionCommandInput extends GetFunctionRequest {}
export type GetFunctionCommandOutputType = Pick<
  GetFunctionResult,
  Exclude<keyof GetFunctionResult, "FunctionCode">
> & {
  FunctionCode?: Uint8ArrayBlobAdapter;
};
export interface GetFunctionCommandOutput
  extends GetFunctionCommandOutputType,
    __MetadataBearer {}
export declare class GetFunctionCommand extends $Command<
  GetFunctionCommandInput,
  GetFunctionCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetFunctionCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetFunctionCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<GetFunctionCommandInput, GetFunctionCommandOutput>;
  private serialize;
  private deserialize;
}
